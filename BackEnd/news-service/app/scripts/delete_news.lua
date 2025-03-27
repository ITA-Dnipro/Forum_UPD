local key = KEYS[1]
local news_id = tostring(ARGV[1])

redis.log(redis.LOG_NOTICE, "Attempting to delete news ID: " .. news_id)

-- Check if the key exists
if redis.call("EXISTS", key) == 0 then
    redis.log(redis.LOG_NOTICE, "Cache does not exist, nothing to delete")
    return 0
end

redis.log(redis.LOG_NOTICE, "Cache exist: ")

local cached_news = redis.call("LRANGE", key, 0, -1)
local found = false

for _, article_json in ipairs(cached_news) do
    local success, article = pcall(cjson.decode, article_json)

    redis.log(redis.LOG_NOTICE, "Success: " .. tostring(success))
    redis.log(redis.LOG_NOTICE, "TYPE: " .. tostring(type(article)))
    redis.log(redis.LOG_NOTICE, "Article id: " .. tostring(article["id"]))

    if success and type(article) == "table" and article["id"] then
        if tostring(article["id"]) == news_id then
            redis.call("LREM", key, 1, article_json)
            found = true
            redis.log(redis.LOG_NOTICE, "Deleted article ID: " .. news_id)
            break
        end
    else
        redis.log(redis.LOG_NOTICE, "Invalid article structure, skipping")
    end
end

if not found then
    redis.log(redis.LOG_NOTICE, "No matching article found in cache")
    return 0
end

-- Preserve TTL
local ttl = redis.call("TTL", key)
if ttl == -1 then
    redis.call("EXPIRE", key, 57600)
end

return "DELETED"
