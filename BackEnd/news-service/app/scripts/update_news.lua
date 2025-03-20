local key = KEYS[1]
local max_size = tonumber(ARGV[table.getn(ARGV)]) -- Last argument is max_size
local ttl = 57600

redis.log(redis.LOG_NOTICE, "Entering Lua script for updating news cache")

-- Loop through all arguments except the last one (which is max_size)
for i = 1, table.getn(ARGV) - 1 do
    redis.call("RPUSH", key, ARGV[i])
end

redis.log(redis.LOG_NOTICE, "Pushed new articles")

-- Trim the list to ensure it does not exceed max size
redis.call("LTRIM", key, -max_size, -1)

redis.call("EXPIRE", key, ttl)
redis.log(redis.LOG_NOTICE, "TTL reset to " .. ttl .. " seconds")

redis.log(redis.LOG_NOTICE, "Cache updated successfully")

return "Updated"
