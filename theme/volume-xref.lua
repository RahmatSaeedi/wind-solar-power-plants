-- theme/volume-xref.lua — cross-volume references for the per-volume editions.
--
-- The website and the full-book build contain every chapter, so every
-- @sec-/@fig-/@tbl-/@eq-/@exm-/@exr- reference resolves. A printed or e-book
-- VOLUME contains only some chapters; a reference to a label in another
-- volume would print as "?@sec-ch04-a-betz". This filter, run before Quarto's
-- own cross-referencing (at: pre-quarto), replaces such a reference with plain
-- Persian text naming the chapter and the volume:
--
--   @sec-ch04-a-betz   ->  فصلِ ۴، جلدِ ۱
--   @fig-ch10-poa      ->  شکلی در فصلِ ۱۰، جلدِ ۲
--   @exr-appx-3        ->  تمرینی در پیوستِ X، جلدِ ۹
--
-- It does nothing unless the document metadata has a `bookvolume` map, which
-- only the volume profile written by tools/build_volume.py sets:
--
--   bookvolume:
--     n: 2                      # this volume
--     map: "1:1-5;2:6-11;..."   # volume:first-last chapter, ';'-separated
--     appendices: 9             # the volume that holds the appendices
--
-- Labels carry their chapter (sec-ch04-..., exm-ch11-...) or appendix
-- (sec-app-x-..., exr-appx-...) by the book's naming rule (CLAUDE.md), so no
-- index of labels is needed.

local FA_DIGITS = { ["0"] = "۰", ["1"] = "۱", ["2"] = "۲", ["3"] = "۳", ["4"] = "۴",
                    ["5"] = "۵", ["6"] = "۶", ["7"] = "۷", ["8"] = "۸", ["9"] = "۹" }

local KIND = { fig = "شکلی در ", tbl = "جدولی در ", eq = "معادله‌ای در ",
               exm = "مثالی در ", exr = "تمرینی در ", sec = "" }

local this_volume, appendix_volume = nil, nil
local volume_of = {}          -- chapter number -> volume number

local function fa(n)
  return (tostring(n):gsub("%d", FA_DIGITS))
end

local function read_meta(meta)
  local v = meta.bookvolume
  if v == nil then return end
  this_volume = tonumber(pandoc.utils.stringify(v.n))
  appendix_volume = tonumber(pandoc.utils.stringify(v.appendices or v.n))
  local map = pandoc.utils.stringify(v.map or "")
  for vol, first, last in map:gmatch("(%d+):(%d+)%-(%d+)") do
    for ch = tonumber(first), tonumber(last) do
      volume_of[ch] = tonumber(vol)
    end
  end
end

-- (kind, place text, volume) for a label, or nil when it is not a book label
local function locate(id)
  local kind, ch = id:match("^(%a+)%-ch(%d%d)")
  if kind and KIND[kind] then
    local n = tonumber(ch)
    return kind, "فصلِ " .. fa(n), volume_of[n]
  end
  local k3 = id:match("^(%a+)%-appx%-")          -- exr-appx-N: appendix X
  if k3 and KIND[k3] then
    return k3, "پیوستِ X", appendix_volume
  end
  local k2, letter = id:match("^(%a+)%-app%-(%a)")
  if k2 and KIND[k2] then
    return k2, "پیوستِ " .. letter:upper(), appendix_volume
  end
  return nil
end

local function replace(cite)
  if this_volume == nil then return nil end
  local parts, changed = {}, false
  for i, c in ipairs(cite.citations) do
    local kind, place, vol = locate(c.id)
    if kind and vol and vol ~= this_volume then
      parts[#parts + 1] = KIND[kind] .. place .. "، جلدِ " .. fa(vol)
      changed = true
    else
      parts[#parts + 1] = false
    end
  end
  if not changed then return nil end
  -- keep same-volume references of a mixed citation as their own Cite
  local out = pandoc.List()
  for i, c in ipairs(cite.citations) do
    if i > 1 then out:insert(pandoc.Str("، ")) end
    if parts[i] then
      out:insert(pandoc.Span({ pandoc.Str(parts[i]) }, { class = "xvol" }))
    else
      out:insert(pandoc.Cite({ pandoc.Str("@" .. c.id) }, { c }))
    end
  end
  return out
end

-- Several references to sections of one chapter in another volume read
-- "فصلِ ۴، جلدِ ۱، فصلِ ۴، جلدِ ۱": keep the first of a run of equal texts
-- joined only by commas, "و", spaces or line breaks.
local function is_sep(el)
  if el.t == "Space" or el.t == "SoftBreak" then return true end
  if el.t == "Str" then
    return el.text == "،" or el.text == "," or el.text == "و" or el.text == "،،"
  end
  return false
end

local function xvol_text(el)
  if el and el.t == "Span" and el.classes:includes("xvol") then
    return pandoc.utils.stringify(el)
  end
  return nil
end

local function dedupe(inlines)
  if this_volume == nil then return nil end
  local out, last_idx = pandoc.List(), nil
  for _, el in ipairs(inlines) do
    local t = xvol_text(el)
    if t and last_idx and xvol_text(out[last_idx]) == t then
      local only_sep = true
      for k = last_idx + 1, #out do
        if not is_sep(out[k]) then only_sep = false end
      end
      if only_sep then
        while #out > last_idx do out:remove() end     -- drop the separators
        goto continue
      end
    end
    out:insert(el)
    if t then last_idx = #out end
    ::continue::
  end
  -- unwrap the marker spans
  local final = pandoc.List()
  for _, el in ipairs(out) do
    if xvol_text(el) then final:extend(el.content) else final:insert(el) end
  end
  return final
end

return {
  { Meta = function(meta) read_meta(meta) end },
  { Cite = replace },
  { Inlines = dedupe },
}
