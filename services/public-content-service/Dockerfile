# FROM nickblah/lua:5.3-luarocks
# # FROM debian:buster 
# # FROM buildpack-deps:buster 
# # FROM lua:5.3
# # FROM openresty/openresty:1.21.4.1-0-jammy
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     lua5.3 \
#     luarocks \
#     liblua5.3-dev \
#     libssl-dev \
#     && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size
    
# RUN luarocks install luasocket


# #FOR LAPIS 

# # RUN apt-get update && apt-get install -y curl gnupg2 ca-certificates \
# #     && curl -fsSL https://openresty.org/package/pubkey.gpg | apt-key add - \
# #     && echo "deb http://openresty.org/package/debian bullseye main" | tee /etc/apt/sources.list.d/openresty.list \
# #     && apt-get update && apt-get install -y openresty

# #Set the correct Lua version for LuaRocks (use LuaJIT from OpenResty)
# # ENV LUA_BIN=/usr/local/openresty/luajit/bin/luajit
# # ENV LUA_LIB=/usr/local/openresty/luajit/lib/luajit-2.1.0-beta3

# RUN luarocks install luaossl
# # RUN luarocks install lapis 
# # RUN rm -rf /var/lib/apt/lists/*
# #END

# WORKDIR /app
# COPY ./src /app
# EXPOSE 8085
# CMD ["lua", "main-hw.lua"]

# # FOR LAPIS 
# # CMD ["lapis", "server", "start"]





FROM openresty/openresty:1.21.4.1-0-jammy
RUN apt-get update && apt-get install -y \
    build-essential \
    luarocks \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size
RUN luarocks install luaossl  # If you need SSL support
WORKDIR /app
COPY ./src /app
EXPOSE 8085
CMD ["openresty", "-g", "daemon off;", "-c", "/app/nginx.conf"]





