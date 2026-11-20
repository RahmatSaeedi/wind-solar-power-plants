-- theme/include-code.lua — print code and program output straight from the
-- tested companion files, so the book can never drift from what was run.
--
-- Usage in .qmd (paths are relative to the project root):
--
--   ```{.python include="companion/ch06/voltage_drop.py"}
--   ```
--   ```{.python include="companion/plantp/units.py" start="# [start: to_si]" end="# [end: to_si]"}
--   ```
--   ```{.text include="companion/ch06/expected/voltage_drop.txt"}
--   ```
--
--   ```{.python include="companion/plantp/dc.py" function="voltage_drop"}
--   ```
--
-- * `function="name"` prints one top-level Python `def` or `class` (with its
--   decorators), up to the next top-level statement.
-- * `start` / `end` are marker lines inside the file; the lines BETWEEN them
--   are printed (the markers themselves are not). Either may be omitted.
-- * Without any of these the whole file is printed, minus a leading shebang line.
-- * A missing file, function or marker stops the render with a clear message.
-- Must run before theme/ltr.lua (which wraps code blocks for the PDF).

local function project_dir()
  if quarto and quarto.project and quarto.project.directory then
    return quarto.project.directory
  end
  return os.getenv("QUARTO_PROJECT_DIR") or "."
end

local function read_lines(path)
  local fh = io.open(path, "r")
  if not fh then
    error("include-code.lua: cannot open '" .. path .. "'")
  end
  local lines = {}
  for line in fh:lines() do
    lines[#lines + 1] = (line:gsub("\r$", ""))
  end
  fh:close()
  return lines
end

-- Markers are compared with leading/trailing space removed and inner runs of
-- spaces collapsed, so a column-aligned report line can be quoted loosely.
local function trim(s)
  return (s:gsub("^%s+", ""):gsub("%s+$", ""):gsub("%s+", " "))
end

function CodeBlock(el)
  local rel = el.attributes["include"]
  if not rel then return nil end
  local path = project_dir() .. "/" .. rel
  -- the attributes are `start` and `end`; any other spelling would be
  -- ignored silently and print the whole file, so it is an error
  for _, bad in ipairs({"start-after", "end-before", "start-line", "end-line"}) do
    if el.attributes[bad] then
      error("include-code.lua: unknown attribute '" .. bad .. "' in " .. rel ..
            " (use start= and end=)")
    end
  end
  local lines = read_lines(path)
  local start_marker = el.attributes["start"]
  local end_marker = el.attributes["end"]
  local func = el.attributes["function"]
  local first, last = 1, #lines

  if func then
    local found
    for i, line in ipairs(lines) do
      local name = line:match("^def%s+([%w_]+)%s*%(") or line:match("^class%s+([%w_]+)")
      if name == func then found = i; break end
    end
    if not found then
      error("include-code.lua: function '" .. func .. "' not found in " .. rel)
    end
    first = found
    while first > 1 and lines[first - 1]:match("^@") do first = first - 1 end
    last = #lines
    for i = found + 1, #lines do
      -- a new top-level statement ends the block; ")" closes a multi-line signature
      if lines[i]:match("^%S") and not lines[i]:match("^%)") then last = i - 1; break end
    end
    start_marker, end_marker = nil, nil
  end

  if start_marker then
    first = nil
    for i, line in ipairs(lines) do
      if trim(line) == trim(start_marker) then first = i + 1; break end
    end
    if not first then
      error("include-code.lua: start marker '" .. start_marker .. "' not found in " .. rel)
    end
  end
  if end_marker then
    last = nil
    for i = first, #lines do
      if trim(lines[i]) == trim(end_marker) then last = i - 1; break end
    end
    if not last then
      error("include-code.lua: end marker '" .. end_marker .. "' not found in " .. rel)
    end
  end
  if not start_marker and not func and lines[first] and lines[first]:match("^#!") then
    first = first + 1
  end
  -- drop blank lines at both ends
  while first <= last and trim(lines[first]) == "" do first = first + 1 end
  while last >= first and trim(lines[last]) == "" do last = last - 1 end

  local out = {}
  for i = first, last do out[#out + 1] = lines[i] end
  el.text = table.concat(out, "\n")
  el.attributes["include"] = nil
  el.attributes["start"] = nil
  el.attributes["end"] = nil
  el.attributes["function"] = nil
  return el
end
