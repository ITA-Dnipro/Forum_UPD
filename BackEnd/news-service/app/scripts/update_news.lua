local key = KEYS[1]
local max_size = tonumber(ARGV[table.getn(ARGV)]) -- Last argument is max_size
local ttl = 57600

redis.log(redis.LOG_NOTICE, "Entering Lua script for updating news cache")

-- Loop through all arguments except the last one (which is max_size)
for i = 1, table.getn(ARGV) - 1 do
    redis.call("LPUSH", key, ARGV[i])
end

redis.log(redis.LOG_NOTICE, "Pushed new articles")

-- Trim the list to ensure it does not exceed max size
redis.call("LTRIM", key, 0, max_size - 1) -- 0-based index

-- Set TTL (only if the key is newly created)
if redis.call("TTL", key) == -1 then
    redis.call("EXPIRE", key, ttl)
end

redis.log(redis.LOG_NOTICE, "Cache updated successfully")

return "Updated"
