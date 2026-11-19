-- spike_patch_3d.lua
-- grandMA3 2.5.1 spike: patch 1 mover + 1 wash, set 3D positions, write readback files.
-- Modeled on ShowPatch.lua:22-68 (hw_test plugin shipped with MA3 2.5.1).
-- Written without access to a running MA3. Run only in a NEW SCRATCH SHOW in onPC.
--
-- Output files (in GetPath(Enums.PathType.Library), i.e. gma3_library):
--   spike_patch_3d_log.txt                  step-by-step log, always written
--   spike_patch_3d_readback.json            hand-built JSON via io.open, always written
--   spike_patch_3d_readback_exportjson.json same table via ExportJson (may be malformed per MA docs)

-- Plugin component convention (same as startshow_import.lua / performance3d.lua).
local pluginName    = select(1, ...)
local componentName = select(2, ...)
local signalTable   = select(3, ...)
local myHandle      = select(4, ...)

---------------------------------------------------------------------------
-- Configuration
---------------------------------------------------------------------------
local MOVER_CANDIDATES = { "Moving Head", "Moving Head 1", "Generic Moving Head", "Moving Light" }
local WASH_CANDIDATES  = { "LED - IRGBW", "LED - RGBW", "LED - RGB" }

local FIXTURES = {
  { role = "mover", fid = 1,   patch = "1.1",   posX = -3, posY =  2, posZ = 6, rot = { 15, 30, 45 } },
  { role = "wash",  fid = 101, patch = "1.101", posX =  3, posY = -2, posZ = 6, rot = { 10, 20, 35 } },
}
-- ShowPatch.lua stores from index 2 (assumes index 1 already exists in Stages.1.Fixtures).
-- We do the same: mover = index 2, wash = index 3. Readback identifies fixtures by FID, not index.
local FIRST_STORE_INDEX = 2

local OUT_NAMES = {
  log      = "spike_patch_3d_log.txt",
  json     = "spike_patch_3d_readback.json",
  exportjs = "spike_patch_3d_readback_exportjson.json",
}

---------------------------------------------------------------------------
-- Logging
---------------------------------------------------------------------------
local logLines = {}
local errors   = {}

local function log(msg)
  msg = tostring(msg)
  logLines[#logLines + 1] = msg
  pcall(Echo, msg)
end

local function logErr(where, err)
  local m = "ERROR in " .. where .. ": " .. tostring(err)
  errors[#errors + 1] = m
  log(m)
end

-- Run fn(...) under pcall; log failure; return ok, result.
local function try(where, fn, ...)
  local ok, res = pcall(fn, ...)
  if not ok then logErr(where, res) end
  return ok, res
end

-- Pause so the Lua task lets the main task catch up (ShowPatch.lua uses coroutine:yield(1)).
local function pause(seconds)
  -- UNVERIFIED: coroutine.yield(seconds) semantics; ShowPatch.lua writes `coroutine:yield(1)`.
  pcall(coroutine.yield, seconds or 0.2)
end

-- Cmd wrapper: logs command and feedback, never throws.
local function cmd(str)
  local ok, res = pcall(Cmd, str)
  if not ok then
    logErr("Cmd(" .. str .. ")", res)
    return nil
  end
  log("Cmd: " .. str .. "  ->  " .. tostring(res))
  return res
end

---------------------------------------------------------------------------
-- Object helpers
---------------------------------------------------------------------------
local function safeGet(obj, prop)
  if obj == nil then return nil end
  local ok, v = pcall(function() return obj:Get(prop) end)
  if ok then return v end
  return nil
end

local function safeName(obj)
  local ok, v = pcall(function() return obj.name end)
  if ok and v ~= nil then return tostring(v) end
  return nil
end

local function safeChildren(obj)
  if obj == nil then return {} end
  local ok, v = pcall(function() return obj:Children() end)
  if ok and type(v) == "table" then return v end
  return {}
end

local function safeCount(obj)
  if obj == nil then return nil end
  local ok, v = pcall(function() return obj:Count() end)
  if ok then return v end
  return nil
end

-- Dump every property of obj into a table name -> string value.
-- PropertyCount/PropertyName are 0-based (see systemtests/help/system_test_helping_functions_db.lua:34-37).
local function dumpProperties(obj)
  local props = {}
  if obj == nil then return props end
  local okC, n = pcall(function() return obj:PropertyCount() end)
  if not okC or type(n) ~= "number" then return props end
  for i = 0, n - 1 do
    local okN, pname = pcall(function() return obj:PropertyName(i) end)
    if okN and pname ~= nil then
      pname = tostring(pname)
      local v = safeGet(obj, pname)
      props[pname] = (v == nil) and "" or tostring(v)
    end
  end
  return props
end

local function sortedKeys(t)
  local keys = {}
  for k in pairs(t) do keys[#keys + 1] = k end
  table.sort(keys)
  return keys
end

local function nameSet(children)
  local s = {}
  for _, c in ipairs(children) do
    local nm = safeName(c)
    if nm then s[nm] = true end
  end
  return s
end

---------------------------------------------------------------------------
-- Show navigation
---------------------------------------------------------------------------
local function fixtureTypes()
  return Root().ShowData.Patch.FixtureTypes
end

local function stageFixtures()
  return Root().ShowData.Patch.Stages[1].Fixtures
end

---------------------------------------------------------------------------
-- Step 1: import library fixture types
---------------------------------------------------------------------------
-- Returns the name of the fixture type that appeared in the show, or nil.
-- Library name and resulting show-object name may differ, so detect the new child by diffing names.
local function importFixtureType(label, candidates, report)
  report[label] = { attempts = {} }
  for _, libName in ipairs(candidates) do
    local before = nameSet(safeChildren(fixtureTypes()))
    local result, newName
    for retry = 0, 3 do
      result = cmd("import lib '" .. libName .. "'")
      pause(0.5)
      for _, c in ipairs(safeChildren(fixtureTypes())) do
        local nm = safeName(c)
        if nm and not before[nm] then newName = nm end
      end
      if newName or (result ~= "OK" and retry >= 1) then break end
    end
    local attempt = { libName = libName, cmdResult = tostring(result), newTypeName = newName }
    table.insert(report[label].attempts, attempt)
    log(string.format("Import attempt [%s] lib '%s': cmd=%s newType=%s",
      label, libName, tostring(result), tostring(newName)))
    if newName then
      report[label].libName = libName
      report[label].typeName = newName
      return newName
    end
  end
  log("No candidate library name worked for " .. label)
  return nil
end

---------------------------------------------------------------------------
-- Step 3: enumerate modes
---------------------------------------------------------------------------
local function enumerateModes(typeName)
  local modes = {}
  local ft = fixtureTypes():Find(typeName)
  if not IsObjectValid(ft) then
    log("Fixture type not found for mode enumeration: " .. tostring(typeName))
    return modes, nil
  end
  -- DMXModes / DMXChannels: seen in systemtests/system_test_framework.lua:2240, 2331.
  local okM, dmxModes = pcall(function() return ft.DMXModes end)
  local modeObjs = okM and safeChildren(dmxModes) or {}
  for _, m in ipairs(modeObjs) do
    local chCount
    local okCh, chans = pcall(function() return m.DMXChannels end)
    if okCh and chans ~= nil then chCount = safeCount(chans) end
    modes[#modes + 1] = { name = safeName(m) or "?", channelCount = chCount, handle = m }
    log(string.format("  type '%s' mode '%s' channels=%s", typeName, safeName(m) or "?", tostring(chCount)))
  end
  if #modes == 0 then log("  type '" .. typeName .. "': no modes found via DMXModes") end
  return modes, ft
end

---------------------------------------------------------------------------
-- Main flow
---------------------------------------------------------------------------
local report = {
  plugin = "spike_patch_3d",
  ma3_target_version = "2.5.1",
  imports = {},
  modes = {},        -- typeName -> list of { name, channelCount }
  chosenModes = {},  -- role -> mode name
  fixtures = {},
  errors = errors,
  assumptions = {
    "Stages.1.Fixtures index 1 pre-exists; fixtures stored from index " .. FIRST_STORE_INDEX .. " as in ShowPatch.lua",
  },
}

local function stepImport()
  cmd("cd Root")
  cmd("cd 'ShowData'.'Patch'")
  cmd("set 'FixtureTypes' 'Source'='library'")
  cmd("cd 'FixtureTypes'")
  -- UNVERIFIED in 2.5.1: ShowPatch.lua sets these CurrentProfile() flags before importing from the library.
  try("CurrentProfile flags", function()
    CurrentProfile().FixtureLibShowMA = true
    CurrentProfile().FixtureLibShowUser = false
    CurrentProfile().FixtureLibShowShare = false
  end)
  importFixtureType("mover", MOVER_CANDIDATES, report.imports)
  importFixtureType("wash", WASH_CANDIDATES, report.imports)
  cmd("cd ..")
end

local typeByRole = {}
local modeObjByRole = {}

local function stepModes()
  for role, typeName in pairs(typeByRole) do
    local modes, _ = enumerateModes(typeName)
    local plain = {}
    for _, m in ipairs(modes) do
      plain[#plain + 1] = { name = m.name, channelCount = m.channelCount }
    end
    report.modes[typeName] = plain
    -- Pick the first mode (documented choice; the probe doc records all modes so the user can choose later).
    if modes[1] then
      report.chosenModes[role] = modes[1].name
      modeObjByRole[role] = modes[1].handle
    end
  end
end

local function stepStore()
  cmd("cd Root")
  cmd("cd 'ShowData'.'Patch'")
  cmd("cd 'Stages'")
  cmd("cd 1")
  cmd("cd 'Fixtures'")
  local last = FIRST_STORE_INDEX + #FIXTURES - 1
  cmd("store " .. FIRST_STORE_INDEX .. " thru " .. last)
  for i, fx in ipairs(FIXTURES) do
    local idx = FIRST_STORE_INDEX + i - 1
    fx.index = idx
    local typeName = typeByRole[fx.role]
    if typeName then
      cmd("Assign FixtureType '" .. typeName .. "' at " .. idx)
    else
      log("Skipping Assign for " .. fx.role .. ": no fixture type imported")
    end
    cmd("Set " .. idx .. " Property 'FID' " .. fx.fid)
    cmd("Set " .. idx .. " 'PosX' " .. fx.posX)
    cmd("Set " .. idx .. " 'PosY' " .. fx.posY)
    cmd("Set " .. idx .. " 'PosZ' " .. fx.posZ)
    local mode = modeObjByRole[fx.role]
    if mode and IsObjectValid(mode) then
      cmd("Set " .. idx .. " property 'Mode' '" .. tostring(HandleToStr(mode)) .. "'")
    else
      log("Skipping Mode set for " .. fx.role .. ": no mode object")
    end
    cmd("Set " .. idx .. " 'Patch' " .. fx.patch)
    pause(0.2)
  end
  cmd("cd Root")
end

-- Try candidate rotation property names. Real names are unknown (UNVERIFIED); the property dump in the
-- readback is the authoritative source for what exists. Only names that exist on the object are set.
local ROT_CANDIDATES = { { "RotX", "RotY", "RotZ" }, { "RotationX", "RotationY", "RotationZ" }, { "Rotx", "Roty", "Rotz" } }

local function stepRotation()
  local children = safeChildren(stageFixtures())
  for _, fx in ipairs(FIXTURES) do
    local obj = children[fx.index]  -- UNVERIFIED: Children() order matches pool index
    local props = dumpProperties(obj)
    local set = false
    for _, names in ipairs(ROT_CANDIDATES) do
      if props[names[1]] ~= nil and props[names[2]] ~= nil and props[names[3]] ~= nil then
        for k = 1, 3 do cmd("Set " .. fx.index .. " '" .. names[k] .. "' " .. fx.rot[k]) end
        fx.rotNames = names
        set = true
        break
      end
    end
    log(string.format("Rotation for %s (index %d): property names %s",
      fx.role, fx.index, set and table.concat(fx.rotNames, "/") or "NOT FOUND (see property dump)"))
  end
end

---------------------------------------------------------------------------
-- Readback
---------------------------------------------------------------------------
local function modeNameOf(fobj)
  -- Mode may be a handle-valued property; try the object route first, then the raw string.
  local ok, m = pcall(function() return fobj.Mode end)
  if ok and m ~= nil then
    local nm = safeName(m)
    if nm then return nm end
  end
  local v = safeGet(fobj, "Mode")
  return v and tostring(v) or nil
end

local function typeNameOf(fobj)
  local ok, t = pcall(function() return fobj.FixtureType end)
  if ok and t ~= nil then
    local nm = safeName(t)
    if nm then return nm end
  end
  local v = safeGet(fobj, "FixtureType")
  return v and tostring(v) or nil
end

local function stepReadback()
  report.fixtures = {}
  local children = safeChildren(stageFixtures())
  report.stageFixtureCount = #children
  for _, f in ipairs(children) do
    local props = dumpProperties(f)
    report.fixtures[#report.fixtures + 1] = {
      name        = safeName(f),
      fid         = safeGet(f, "FID"),
      fixtureType = typeNameOf(f),
      mode        = modeNameOf(f),
      patch       = safeGet(f, "Patch"),
      posX        = safeGet(f, "PosX"),
      posY        = safeGet(f, "PosY"),
      posZ        = safeGet(f, "PosZ"),
      rotX        = safeGet(f, "RotX"),   -- UNVERIFIED property names; see "properties" for real ones
      rotY        = safeGet(f, "RotY"),
      rotZ        = safeGet(f, "RotZ"),
      properties  = props,
    }
  end
  log("Readback: " .. #children .. " fixtures in Stages.1.Fixtures")
end

---------------------------------------------------------------------------
-- Output: hand-built JSON
---------------------------------------------------------------------------
local function jsonString(s)
  s = tostring(s)
  s = s:gsub('[%c"\\]', function(c)
    local map = { ['"'] = '\\"', ['\\'] = '\\\\', ['\n'] = '\\n', ['\r'] = '\\r', ['\t'] = '\\t' }
    return map[c] or string.format("\\u%04x", c:byte())
  end)
  return '"' .. s .. '"'
end

local function isArray(t)
  local n = 0
  for _ in pairs(t) do n = n + 1 end
  return n == #t
end

local function toJson(v, indent)
  indent = indent or ""
  local tv = type(v)
  if v == nil then return "null"
  elseif tv == "boolean" or tv == "number" then return tostring(v)
  elseif tv == "string" then return jsonString(v)
  elseif tv == "table" then
    local inner = indent .. "  "
    local parts = {}
    if isArray(v) then
      for _, item in ipairs(v) do parts[#parts + 1] = inner .. toJson(item, inner) end
      if #parts == 0 then return "[]" end
      return "[\n" .. table.concat(parts, ",\n") .. "\n" .. indent .. "]"
    end
    for _, k in ipairs(sortedKeys(v)) do
      parts[#parts + 1] = inner .. jsonString(k) .. ": " .. toJson(v[k], inner)
    end
    return "{\n" .. table.concat(parts, ",\n") .. "\n" .. indent .. "}"
  end
  return jsonString(tostring(v))  -- userdata/functions
end

local function writeFile(path, text)
  local f, err = io.open(path, "w")
  if not f then return false, err end
  f:write(text)
  f:close()
  return true
end

local function writeOutputs()
  local dir
  local okDir, d = pcall(function() return GetPath(Enums.PathType.Library) end)
  if okDir and d then dir = d else
    logErr("GetPath(Library)", d)
    dir = "."
  end
  local sep = "/"  -- UNVERIFIED on Windows; the doc examples concatenate "/" as well
  local paths = {
    log      = dir .. sep .. OUT_NAMES.log,
    json     = dir .. sep .. OUT_NAMES.json,
    exportjs = dir .. sep .. OUT_NAMES.exportjs,
  }
  report.outputPaths = paths

  -- 1) hand-built JSON (most likely to work).
  local okJ, errJ = try("hand JSON", function()
    local ok, e = writeFile(paths.json, toJson(report))
    if not ok then error(e) end
  end)
  log("Readback JSON (hand-built): " .. paths.json .. (okJ and "" or "  FAILED"))

  -- 2) ExportJson of the same table (documented; may be malformed per docs).
  try("ExportJson", function()
    local ok = ExportJson(paths.exportjs, report)
    log("ExportJson(" .. paths.exportjs .. ") returned " .. tostring(ok))
  end)

  -- 3) Log last so it contains everything above.
  log("Log file: " .. paths.log)
  local okL, errL = writeFile(paths.log, table.concat(logLines, "\n") .. "\n")
  if not okL then pcall(Echo, "Log write failed: " .. tostring(errL)) end
end

---------------------------------------------------------------------------
-- Entry point
---------------------------------------------------------------------------
local function run()
  log("spike_patch_3d starting")
  try("version", function()
    local b = BuildDetails()
    report.build = b
  end)
  try("import", stepImport)
  typeByRole.mover = report.imports.mover and report.imports.mover.typeName
  typeByRole.wash  = report.imports.wash and report.imports.wash.typeName
  try("modes", stepModes)
  try("store", stepStore)
  try("rotation", stepRotation)
  try("readback", stepReadback)
  try("cd Root", function() Cmd("cd Root") end)
  writeOutputs()
  log("spike_patch_3d done. errors=" .. #errors)
end

return function()
  local ok, err = pcall(run)
  if not ok then
    logErr("run", err)
    pcall(writeOutputs)
  end
end
