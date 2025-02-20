local function say_hello()
    return "Hello from Lua in OpenResty!"
end

return {
    say_hello = say_hello
}
