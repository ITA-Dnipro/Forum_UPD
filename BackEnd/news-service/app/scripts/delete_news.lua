local key = KEYS[1]
local news_id = tostring(ARGV[1])

redis.log(redis.LOG_NOTICE, "Deleting news ID: " .. news_id)


local cached_news = redis.call("GET", key)
if not cached_news then
    redis.log(redis.LOG_NOTICE, "Cache does not exist, nothing to delete")
    return 0
end

redis.log(redis.LOG_NOTICE, "Cache found, full JSON: " .. cached_news)

local success, news_wrapper = pcall(cjson.decode, cached_news)
if not success then
    redis.log(redis.LOG_NOTICE, "Failed to decode JSON")
    return 0
end


if type(news_wrapper) ~= "table" or #news_wrapper == 0 then
    redis.log(redis.LOG_NOTICE, "Cache structure is not a valid list")
    return 0
end

local news_list = news_wrapper[1]

if type(news_list) ~= "table" then
    redis.log(redis.LOG_NOTICE, "Extracted value is not a list")
    return 0
end

redis.log(redis.LOG_NOTICE, "Successfully decoded JSON, total articles: " .. tostring(#news_list))

local updated_news_list = {}
local found = false

for _, article in ipairs(news_list) do
    redis.log(redis.LOG_NOTICE, "Full article JSON: " .. cjson.encode(article))

    if type(article) == "table" then
        local article_id = tostring(article["id"])
        
        if article_id then
            redis.log(redis.LOG_NOTICE, "Checking article ID: " .. article_id)
            if article_id ~= news_id then
                table.insert(updated_news_list, article)
            else
                redis.log(redis.LOG_NOTICE, "Found and deleting article ID: " .. article_id)
                found = true
            end
        else
            redis.log(redis.LOG_NOTICE, "Article has no ID field, skipping")
        end
    end
end

if not found then
    redis.log(redis.LOG_NOTICE, "No matching article found in cache")
end

local ttl = redis.call("TTL", key)
if ttl <= 0 then
    ttl = 57600
    redis.log(redis.LOG_NOTICE, "TTL was invalid, setting to default: " .. ttl)
end

if #updated_news_list > 0 then
    redis.call("SETEX", key, ttl, cjson.encode({updated_news_list}))  -- Wrap back into a list
    redis.log(redis.LOG_NOTICE, "Updated cache after deletion")
else
    redis.call("DEL", key)
    redis.log(redis.LOG_NOTICE, "Cache is empty, deleting key")
end

return "DELETED"
