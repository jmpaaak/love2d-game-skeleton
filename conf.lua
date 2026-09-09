function love.conf(t)
    local headless = os.getenv("GAME_HEADLESS") == "1"
    local scale = math.max(1, math.min(4, math.floor(tonumber(os.getenv("GAME_SCALE")) or 3)))

    t.identity = "love2d-game-skeleton"
    t.version = "11.5"
    if headless then
        t.window = false
        t.modules.audio = false
        t.modules.window = false
        t.modules.graphics = false
        return
    end
    t.window.title = "LÖVE2D Game Skeleton"
    t.window.width = 320 * scale
    t.window.height = 180 * scale
    t.window.resizable = true
    t.window.highdpi = true
    t.window.vsync = 1
    t.window.msaa = 0
end
