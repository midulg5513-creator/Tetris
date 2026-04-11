import pygame
import random
import sys
import math
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
BOMB_COLOR = (255, 100, 0)  

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1]]  # 炸弹方块
]

# 颜色定义
COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, GREEN, RED, BOMB_COLOR]

# 炸弹方块生成概率 (1/15)
BOMB_PROBABILITY = 1 / 15

# 设置游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块 ")

# 游戏区域左上角坐标
GAME_AREA_X = (SCREEN_WIDTH - SIDEBAR_WIDTH - GRID_WIDTH * GRID_SIZE) // 2
GAME_AREA_Y = (SCREEN_HEIGHT - GRID_HEIGHT * GRID_SIZE) // 2

# 字体加载函数
def get_font(size):
    font_names = ["simhei", "microsoftyahei", "kaiti", "simsunnsimsun", "Arial"]
    for name in font_names:
        try:
            font = pygame.font.SysFont(name, size)
            test_surface = font.render("测试", True, (255, 255, 255))
            if test_surface.get_width() > 0:
                return font
        except:
            continue
    return pygame.font.Font(None, size)

class Tetromino:
    def __init__(self):
        # 随机决定是否生成炸弹方块
        if random.random() < BOMB_PROBABILITY:
            self.shape_index = 7  
        else:
            self.shape_index = random.randint(0, 6) 
            
        self.shape = [row[:] for row in SHAPES[self.shape_index]] 
        self.color = COLORS[self.shape_index]
        
        # 设置初始位置
        if self.shape_index == 7: 
            self.x = GRID_WIDTH // 2
            self.y = 0
        else:
            self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
            self.y = 0
        
    def rotate(self):
        #实现矩阵旋转
        if self.shape_index == 7:
            return
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]         
        return rotated
    
    def draw(self, surface):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        GAME_AREA_X + (self.x + x) * GRID_SIZE,
                        GAME_AREA_Y + (self.y + y) * GRID_SIZE,
                        GRID_SIZE, GRID_SIZE
                    )
                    
                    # 炸弹方块特殊绘制
                    if self.shape_index == 7:
                        pygame.draw.rect(surface, self.color, rect)
                        pygame.draw.rect(surface, WHITE, rect, 1)
                        fuse_rect = pygame.Rect(
                            GAME_AREA_X + (self.x + x) * GRID_SIZE + GRID_SIZE // 2 - 2,
                            GAME_AREA_Y + (self.y + y) * GRID_SIZE - 5,
                            4, 8
                        )
                        pygame.draw.rect(surface, YELLOW, fuse_rect)
                        spark_points = [
                            (GAME_AREA_X + (self.x + x) * GRID_SIZE + GRID_SIZE // 2, 
                             GAME_AREA_Y + (self.y + y) * GRID_SIZE - 10),
                            (GAME_AREA_X + (self.x + x) * GRID_SIZE + GRID_SIZE // 2 - 5, 
                             GAME_AREA_Y + (self.y + y) * GRID_SIZE - 15),
                            (GAME_AREA_X + (self.x + x) * GRID_SIZE + GRID_SIZE // 2 + 5, 
                             GAME_AREA_Y + (self.y + y) * GRID_SIZE - 15)
                        ]
                        pygame.draw.polygon(surface, YELLOW, spark_points)
                    else:
                        # 普通方块绘制
                        pygame.draw.rect(surface, self.color, rect)
                        pygame.draw.rect(surface, WHITE, rect, 1)
                        highlight = pygame.Rect(
                            GAME_AREA_X + (self.x + x) * GRID_SIZE + 2,
                            GAME_AREA_Y + (self.y + y) * GRID_SIZE + 2,
                            GRID_SIZE - 4, GRID_SIZE - 4
                        )
                        pygame.draw.rect(surface, self._adjust_color(self.color, 50), highlight, 1)
    
    def _adjust_color(self, color, adjustment):
        return tuple(max(0, min(255, c + adjustment)) for c in color)

class Game:
    def __init__(self):
        # 使用二维列表表示游戏网格
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  
        self.fall_time = 0
        self.paused = False  
        
        # 爆炸效果相关
        self.explosion_active = False
        self.explosion_time = 0
        self.explosion_positions = []
        
        # 按键状态跟踪
        self.key_states = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_DOWN: False,
            pygame.K_a: False,  
            pygame.K_d: False,
            pygame.K_s: False
        }
        
        # 按键重复延迟和间隔
        self.key_delay = 0.15  
        self.key_interval = 0.05  
        self.key_timers = {
            pygame.K_LEFT: 0,
            pygame.K_RIGHT: 0,
            pygame.K_DOWN: 0,
            pygame.K_a: 0,
            pygame.K_d: 0,
            pygame.K_s: 0
        }
        
        # 使用字体文件创建字体对象
        try:
            self.font = pygame.font.Font("simhei.ttf", 36)
            self.small_font = pygame.font.Font("simhei.ttf", 24)
            self.big_font = pygame.font.Font("simhei.ttf", 64)
        except:
            self.font = get_font(36)
            self.small_font = get_font(24)
            self.big_font = get_font(64)
        
    def new_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()
        
        # 检查游戏是否结束
        if self.check_collision(self.current_piece):
            self.game_over = True
    
    def check_collision(self, piece, dx=0, dy=0):
        #碰撞检测
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT):
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return True
        return False
    
    def explode_bomb(self, x, y):
        #炸弹爆炸效果 - 清除周围8个格子的方块
        self.explosion_positions = []
        explosion_offsets = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),           (1, 0),
            (-1, 1),  (0, 1),  (1, 1)
        ]
        for dx, dy in explosion_offsets:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                self.grid[new_y][new_x] = 0
                self.explosion_positions.append((new_x, new_y))
        self.explosion_active = True
        self.explosion_time = 0
    
    def lock_piece(self):
        #将方块锁定到网格中
        if self.current_piece.shape_index == 7:
            self.explode_bomb(self.current_piece.x, self.current_piece.y)
            self.new_piece()
            return
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if self.current_piece.y + y >= 0:
                        self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color
        self.clear_lines()
        self.new_piece()
    
    def clear_lines(self):
        #检测和清除完整的行
        lines_to_clear = []
        for y, row in enumerate(self.grid):
            if all(row):
                lines_to_clear.append(y)
        for line in sorted(lines_to_clear, reverse=True):
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        # 更新分数和等级
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += (1, 2, 5, 10)[min(len(lines_to_clear)-1, 3)] * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
    
    def move(self, dx, dy):
        if not self.check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate_piece(self):
        # 炸弹方块不需要旋转
        if self.current_piece.shape_index == 7:
            return
            
        rotated_shape = self.current_piece.rotate()
        original_shape = self.current_piece.shape
        
        # 尝试旋转
        self.current_piece.shape = rotated_shape
        
        # 如果旋转后发生碰撞，尝试左右移动以调整位置
        if self.check_collision(self.current_piece):
            if not self.check_collision(self.current_piece, -1, 0):
                self.current_piece.x -= 1
            elif not self.check_collision(self.current_piece, 1, 0):
                self.current_piece.x += 1
            else:
                self.current_piece.shape = original_shape
    
    def update(self, dt):
        if self.game_over or self.paused:
            return
        # 更新爆炸效果
        if self.explosion_active:
            self.explosion_time += dt
            if self.explosion_time >= 0.5: 
                self.explosion_active = False
        # 更新方块自动下落
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.move(0, 1):
                self.lock_piece()
        # 处理持续按键
        for key in [pygame.K_LEFT, pygame.K_a]:
            if self.key_states[key]:
                self.key_timers[key] += dt
                if self.key_timers[key] >= (self.key_delay if self.key_timers[key] == dt else self.key_interval):
                    if self.move(-1, 0):
                        self.key_timers[key] = 0      
        for key in [pygame.K_RIGHT, pygame.K_d]:
            if self.key_states[key]:
                self.key_timers[key] += dt
                if self.key_timers[key] >= (self.key_delay if self.key_timers[key] == dt else self.key_interval):
                    if self.move(1, 0):
                        self.key_timers[key] = 0
        for key in [pygame.K_DOWN, pygame.K_s]:
            if self.key_states[key]:
                self.key_timers[key] += dt
                if self.key_timers[key] >= (self.key_delay if self.key_timers[key] == dt else self.key_interval):
                    if self.move(0, 1):
                        self.key_timers[key] = 0
    
    def toggle_pause(self):
        #切换暂停状态
        self.paused = not self.paused
    
    def reset(self):
        #重置游戏
        self.__init__()
    
    def draw_explosion(self, surface):
        #绘制爆炸效果
        if not self.explosion_active:
            return
        progress = min(1.0, self.explosion_time / 0.5)
        for x, y in self.explosion_positions:
            radius = int(GRID_SIZE * 0.7 * progress)
            center_x = GAME_AREA_X + x * GRID_SIZE + GRID_SIZE // 2
            center_y = GAME_AREA_Y + y * GRID_SIZE + GRID_SIZE // 2
            explosion_color = ( min(255, 255),max(0, int(255 * (1 - progress))),0)
            pygame.draw.circle(surface, explosion_color, (center_x, center_y), radius)
            for angle in range(0, 360, 45):
                end_x = center_x + int(radius * 1.5 * math.cos(math.radians(angle)))
                end_y = center_y + int(radius * 1.5 * math.sin(math.radians(angle)))
                pygame.draw.line(surface, YELLOW, (center_x, center_y), (end_x, end_y), 2)
    
    def draw(self, surface):
        # 绘制游戏区域背景
        game_area = pygame.Rect(GAME_AREA_X, GAME_AREA_Y,  GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE)
        pygame.draw.rect(surface, BLACK, game_area)
        pygame.draw.rect(surface, WHITE, game_area, 2)
        
        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line( surface, DARK_GRAY,(GAME_AREA_X + x * GRID_SIZE, GAME_AREA_Y),(GAME_AREA_X + x * GRID_SIZE, GAME_AREA_Y + GRID_HEIGHT * GRID_SIZE))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(surface, DARK_GRAY,(GAME_AREA_X, GAME_AREA_Y + y * GRID_SIZE),(GAME_AREA_X + GRID_WIDTH * GRID_SIZE, GAME_AREA_Y + y * GRID_SIZE)) 
        # 绘制已固定的方块
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        GAME_AREA_X + x * GRID_SIZE,
                        GAME_AREA_Y + y * GRID_SIZE,
                        GRID_SIZE, GRID_SIZE
                    )
                    pygame.draw.rect(surface, cell, rect)
                    pygame.draw.rect(surface, WHITE, rect, 1)
        
        # 绘制当前下落的方块
        self.current_piece.draw(surface)
        
        # 绘制爆炸效果
        self.draw_explosion(surface)
        
        # 绘制侧边栏
        sidebar = pygame.Rect(
            GAME_AREA_X + GRID_WIDTH * GRID_SIZE + 20, 
            GAME_AREA_Y, 
            SIDEBAR_WIDTH +60, 
            GRID_HEIGHT * GRID_SIZE
        )
        pygame.draw.rect(surface, BLACK, sidebar)
        pygame.draw.rect(surface, WHITE, sidebar, 2)
        
        # 绘制下一个方块预览
        next_text = self.font.render("下一个:", True, WHITE)
        surface.blit(next_text, (sidebar.x + 20, sidebar.y + 20))
        
        # 绘制下一个方块
        next_piece_x = sidebar.x + (sidebar.width - len(self.next_piece.shape[0]) * GRID_SIZE) // 2
        next_piece_y = sidebar.y + 70
        
        for y, row in enumerate(self.next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        next_piece_x + x * GRID_SIZE,
                        next_piece_y + y * GRID_SIZE,
                        GRID_SIZE, GRID_SIZE
                    )
                    pygame.draw.rect(surface, self.next_piece.color, rect)
                    pygame.draw.rect(surface, WHITE, rect, 1)
                    
                    # 如果是炸弹方块，绘制特殊效果
                    if self.next_piece.shape_index == 7:
                        fuse_rect = pygame.Rect(
                            next_piece_x + x * GRID_SIZE + GRID_SIZE // 2 - 2,
                            next_piece_y + y * GRID_SIZE - 5,
                            4, 8
                        )
                        pygame.draw.rect(surface, YELLOW, fuse_rect)
        
        # 绘制分数和等级
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        level_text = self.font.render(f"等级: {self.level}", True, WHITE)
        lines_text = self.font.render(f"消除行: {self.lines_cleared}", True, WHITE)
        
        surface.blit(score_text, (sidebar.x + 20, sidebar.y + 150))
        surface.blit(level_text, (sidebar.x + 20, sidebar.y + 190))
        surface.blit(lines_text, (sidebar.x + 20, sidebar.y + 230))
        
        # 绘制操作说明
        controls_y = sidebar.y + 280
        controls = [
            "操作说明:",
            "←/A →/D : 左右移动",
            "↑/W : 旋转",
            "↓/S : 加速下落",
            "空格 : 直接落下",
            "P : 暂停/继续",
            "R : 重新开始",
            "",
            "特殊方块:",
            "炸弹 - 清除周围",
            "方块 (不计分)"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, WHITE)
            surface.blit(control_text, (sidebar.x + 20, controls_y + i * 30))
        
        # 如果游戏暂停，显示暂停文本
        if self.paused:
            pause_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_surface.fill((0, 0, 0, 128))  
            surface.blit(pause_surface, (0, 0))
            
            pause_text = self.big_font.render("游戏暂停", True, YELLOW)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            surface.blit(pause_text, text_rect)
            
            continue_text = self.font.render("按P键继续", True, WHITE)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            surface.blit(continue_text, continue_rect)
        
        # 如果游戏结束，显示游戏结束文本
        if self.game_over:
            game_over_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            game_over_surface.fill((0, 0, 0, 192))
            surface.blit(game_over_surface, (0, 0))
            
            game_over_text = self.big_font.render("游戏结束!", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            surface.blit(game_over_text, text_rect)
            
            score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(score_text, score_rect)
            
            restart_text = self.font.render("按R键重新开始", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            surface.blit(restart_text, restart_rect)

def main():
    game = Game()
    clock = pygame.time.Clock()
    
    while True:
        dt = clock.tick(60) / 1000.0  
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()
                if event.key == pygame.K_p:
                    game.toggle_pause()
                if event.key in game.key_states:
                    game.key_states[event.key] = True
                    game.key_timers[event.key] = 0
                if not game.paused and not game.game_over:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        while game.move(0, 1):
                            pass
                        game.lock_piece()
            # 按键释放事件
            if event.type == pygame.KEYUP:
                if event.key in game.key_states:
                    game.key_states[event.key] = False
                    game.key_timers[event.key] = 0
        
        # 游戏逻辑更新
        game.update(dt)
        
        # 绘制
        screen.fill((40, 40, 60)) 
        
        # 绘制标题
        title_text = game.big_font.render("俄罗斯方块 ", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_text, title_rect)
        
        game.draw(screen)
        
        pygame.display.flip()

if __name__ == "__main__":
    main()