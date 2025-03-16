local key = KEYS[1]
local new_news = cjson.decode(ARGV[1])
local max_size = tonumber(ARGV[2])
local ttl = 57600

local existing_news = redis.call("GET", key)
local news_list = {}

if existing_news then
    news_list = cjson.decode(existing_news)
end

table.insert(news_list, 1, new_news)

while #news_list > max_size do
    table.remove(news_list)
end


redis.call("SETEX", key, ttl, cjson.encode(news_list))

return "Updated"
