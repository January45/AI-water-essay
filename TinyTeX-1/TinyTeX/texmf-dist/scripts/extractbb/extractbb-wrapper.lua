#!/usr/bin/env texlua
-- extractbb-lua
-- https://github.com/gucci-on-fleek/extractbb
-- SPDX-License-Identifier: MPL-2.0+
-- SPDX-FileCopyrightText: 2024 Max Chernoff
--
-- A generic wrapper to make commands safe to run with restricted shell escape.
--
-- Originally created for extractbb, which is listed in shell_escape_commands,
-- but can be run as dvipdfm(x), which in turn can run arbitrary commands
-- using its -D option.
--
-- The idea is to exec "ebb --ebb <other args>", since only argv[1] is
-- used by dvipdfmx to determine its behavior.
--
-- Note: This script can only adjust the paths and arguments of the target
-- executable; it *CANNOT* make an arbitrary program safe to run with
-- restricted shell escape.

-- A shorter, less paranoid version.
-- (Prepend a hyphen to the line below to enable).
--[=[
arg[0] = arg[0]:gsub("extractbb", "ebb")
table.insert(arg, 1, "ebb")
table.insert(arg, 2, "--extractbb")
os.exec(arg)
os.exit(1)
--]=]

---------------------
--- Configuration ---
---------------------

-- The base name of this script. (Example: ``extractbb'')
local SCRIPT_NAME = "extractbb"

-- The base name of the path to the target program. (Example: ``xdvipdfmx'')
local TARGET_PATH_NAME = "xdvipdfmx"

-- The name to use when calling the target program. Equivalent to ``argv[0]''
-- in C. (Example: ``extractbb'')
local TARGET_EXEC_NAME = "ebb"

-- Any extra arguments to be prepended to the target program, before any
-- user-supplied arguments. Equivalent to ``argv[1], ...'' in C.
-- (Example: ``--extractbb'')
local TARGET_PREPEND_ARGS = { "--extractbb" }

-- Any extra arguments to be appended to the target program, after any
-- user-supplied arguments. Equivalent to ``..., argv[argc]'' in C.
local TARGET_APPEND_ARGS = {}

-- Sets the value of ``openin_any'' to this value. If ``nil'', then the value
-- will be left unchanged. (Example: ``r'')
local READ_PERMS = "r"

-- Sets the value of ``openout_any'' to this value. If ``nil'', then the value
-- will be left unchanged. (Example: ``p'')
local WRITE_PERMS = "p"

-- The name of the Lua interpreter. (Example: ``texlua'')
local INTERPRETER_NAME = "texlua"

-- The extension of the interpreter. Extensionless-names are also permitted.
-- (Example: ``exe'')
local INTERPRETER_EXT = "exe"


----------------------
--- Initialization ---
----------------------

-- Save often-used globals for a slight speed boost.
local insert = table.insert

-- Set the kpathsea program name
kpse.set_program_name(INTERPRETER_NAME, SCRIPT_NAME)

-- Rename the input arguments so we don't get confused
local script_args = arg


----------------------------
--- Function Definitions ---
----------------------------

-- Error messages
local function error(title, details)
    -- Header
    io.stderr:write("! extractbb ERROR: ")
    io.stderr:write(title)
    io.stderr:write(".\n\nTechnical Details:\n")

    -- Messages
    for key, value in pairs(details) do
        io.stderr:write(tostring(key), ": ")
        io.stderr:write("(", type(value), ") ")
        io.stderr:write(tostring(value), "\n")
    end

    -- Traceback
    io.stderr:write("\n")
    io.stderr:write(debug.traceback(nil, 2), "\n")

    -- Flush and exit
    io.stderr:flush()
    os.exit(1)
end

-- Get the directory, name, and extension from a full path. We'll split on
-- either a forward or backward slash---Windows can use either, and we don't
-- need to support Unix systems with TL installed to a directory with
-- backslashes in its name.
local split_dir_pattern = "^(.*)[/\\]([^/\\]-)$"
local split_ext_pattern = "(.*)%.([^.]-)$"

local function split_path(path)
    -- Make sure that we were given a string
    if type(path) ~= "string" then
        return nil, nil, nil
    end

    -- Split the (directory) from the (name and extension)
    local dir, name_ext = path:match(split_dir_pattern)

    -- No directory
    if not dir then
        dir      = nil
        name_ext = path

    -- A bare directory (with a trailing slash)
    elseif name_ext == "" then
        return dir, nil, nil
    end

    -- Split the (name) from the (extension)
    local name, ext = name_ext:match(split_ext_pattern)

    -- No extension (or a dotfile)
    if (not name) or (name == "") then
        name = name_ext
        ext  = nil
    end

    return dir, name, ext
end

-- See if a file exists
local function file_exists(path)
    local mode = lfs.attributes(path, "mode")
    return (mode == "file") or (mode == "link")
end


---------------------
--- Safety Checks ---
---------------------

-- Make sure that we're running unrestricted.
if status.shell_escape ~= 1 then
    error("Shell escape has been disabled", {
        shell_escape = status.shell_escape,
    })
end

if status.safer_option ~= 0 then
    error("The ``safer'' option has been enabled", {
        safer_option = status.safer_option,
    })
end

-- Set the file permissions.
if READ_PERMS then
    os.setenv("openin_any", READ_PERMS)
end

if WRITE_PERMS then
    os.setenv("openout_any", WRITE_PERMS)
end

-- Get the location of the interpreter
local interpreter_dir = os.selfdir or kpse.var_value("SELFAUTOLOC")
local _, interpreter_name, interpreter_ext = split_path(script_args[-1])

if os.type == "windows" then
    interpreter_ext = INTERPRETER_EXT
end

-- Error details
local error_details = {
    interpreter_dir     = interpreter_dir  or "<nil>",
    interpreter_name    = interpreter_name or "<nil>",
    interpreter_ext     = interpreter_ext  or "<nil>",
    os_type             = os.type          or "<nil>",
    os_name             = os.name          or "<nil>",
}

-- Get the path to the target program
local target_ext  = interpreter_ext and ("." .. interpreter_ext) or ""
local target_path = interpreter_dir .. "/" .. TARGET_PATH_NAME .. target_ext

error_details.target_path = target_path or "<nil>"
error_details.target_ext  = target_ext  or "<nil>"

-- Make sure that the target program exists
if not file_exists(target_path) then
    error("The target program does not exist", error_details)
end


----------------------
--- Run the target ---
----------------------

-- Generate the target arguments
local target_args = {
    [0] = target_path,      -- Path to the executable
    [1] = TARGET_EXEC_NAME, -- argv[0]
}

-- argv[2] through argv[n]
for _, arg in ipairs(TARGET_PREPEND_ARGS) do
    insert(target_args, arg)
end

for i = 1, #script_args do
    -- We use a numeric iterator here to avoid ``arg[-1]'' and ``arg[0]''.
    local this_arg = script_args[i]
    insert(target_args, this_arg)

    -- Show version information
    if this_arg:match("%-version") then
        print("[Wrapped by extractbb.lua v1.0.6 (2024-11-21)]") --%%version %%dashdate
    end
end

for _, arg in ipairs(TARGET_APPEND_ARGS) do
    insert(target_args, arg)
end

-- For Unixish OSs, argv is passed as an array into a spawned process, so no
-- further tokenization is done by the C runtime, therefore arguments containing
-- special characters won't cause any issues. For Windows, argv is concatenated
-- into a single string when spawning a new process, then retokenized by the C
-- runtime in the new program, so we need to be careful with special characters
-- here since they might be interpreted as token separators.
if os.type == "windows" then
    for i, arg in ipairs(target_args) do
        -- Hmm, which characters do we need to protect against?
        if arg:match('"') then
            -- Already contains a quote, so let's hope that this means that
            -- someone already quoted it correctly.
        elseif arg:match("[^-_%l%u%d]") then
            -- Contains a special character, so let's quote it.
            target_args[i] = '"' .. arg .. '"'
        end
        -- Any other cases and things should be fine. Probably.
    end
end

-- Run the target program, replacing the current process
local _, err = os.exec(target_args)

-- Unreachable except in the case of a failed exec
for key, value in ipairs(target_args) do
    error_details["target_args[" .. key .. "]"] = value
end

error_details.exec_message = err or "<nil>"
error("The target program failed to run", error_details)
