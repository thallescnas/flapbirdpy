import pygame as game
import os
import random


# init mixer
game.mixer.init()

TELA_LARGURA = 500
TELA_ALTURA = 800

IMG_CANO = game.transform.scale2x(
    game.image.load(os.path.join("imgs", "pipe.png")))
IMG_CHAO = game.transform.scale2x(
    game.image.load(os.path.join("imgs", "base.png")))
IMG_BACK = game.transform.scale2x(
    game.image.load(os.path.join("imgs", "bg.png")))
IMG_PASSARO = [
    game.transform.scale2x(game.image.load(os.path.join("imgs", "bird1.png"))),
    game.transform.scale2x(game.image.load(os.path.join("imgs", "bird2.png"))),
    game.transform.scale2x(game.image.load(os.path.join("imgs", "bird3.png")))
]

game.font.init()
FONT = game.font.SysFont('arial', 50)


def psound(archive, loop=True):
    game.mixer.music.stop()
    game.mixer.music.load(archive)
    game.mixer.music.play(-1 if loop else 0)


class Bird:
    IMGs = IMG_PASSARO
    # animations
    ROTATION_MAX = 25
    SPEED_ROT = 20
    TIMER = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.hight = self.y
        self.time = 0
        self.cont_img = 0
        self.img = self.IMGs[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.hight = self.y

    def move(self):
        # calcular o deslocamento
        self.time += 1
        desloc = 1.5 * (self.time**2) + self.speed * self.time

        # retringir desloc
        if desloc > 16:
            desloc = 16
        elif desloc < 0:
            desloc -= 2
        self.y += desloc

        if desloc < 0 or self.y < (self.hight + 50):
            if self.angle > self.ROTATION_MAX:
                self.angle = self.ROTATION_MAX
        else:
            if self.angle > -90:
                self.angle -= self.SPEED_ROT

    def draw(self, screen):
        # Definar qual imagem do passaro vai aparecer
        self.cont_img += 1
        if self.cont_img < self.TIMER:
            self.img = self.IMGs[0]
        elif self.cont_img < self.TIMER*2:
            self.img = self.IMGs[1]
        elif self.cont_img < self.TIMER*3:
            self.img = self.IMGs[2]
        elif self.cont_img < self.TIMER*4:
            self.img = self.IMGs[1]
        elif self.cont_img < self.TIMER*4 + 1:
            self.img = self.IMGs[0]
            self.cont_img = 0
    # Se o passaro tiver caindo n bater as assas
        if self.angle <= -80:
            self.img = self.IMGs[1]
            self.cont_img = self.TIMER*2

    # Desenhar img
        img_rot = game.transform.rotate(self.img, self.angle)
        pos_centro_img = self.img.get_rect(topleft=(self.x, self.y)).center
        retangulo = img_rot.get_rect(center=pos_centro_img)
        screen.blit(img_rot, retangulo)

    def get_mask(self):
        return game.mask.from_surface(self.img)


class Pipe:
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.hight = 0
        self.pos_top = 0
        self.pos_base = 0
        self.PIPE_TOP = IMG_CANO
        self.PIPE_BASE = game.transform.flip(IMG_CANO, False, True)
        self.passou = False
        self.defi_alt()

    def defi_alt(self):
        self.hight = random.randrange(50, 450)
        self.pos_base = self.hight - self.PIPE_TOP.get_height()
        self.pos_top = self.hight + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.pos_top))
        screen.blit(self.PIPE_BASE, (self.x, self.pos_base))

    def col(self, bird):
        bird_mask = bird.get_mask()
        top_mask = game.mask.from_surface(self.PIPE_TOP)
        base_mask = game.mask.from_surface(self.PIPE_BASE)

        dist_top = (self.x - bird.x, self.pos_top - round(bird.y))
        dist_base = (self.x - bird.x, self.pos_base - round(bird.y))

        top_pont = bird_mask.overlap(top_mask, dist_top)
        base_pont = bird_mask.overlap(base_mask, dist_base)

        if base_pont or top_pont:
            return True
        else:
            return False


class Ground:
    SPEED = 5
    LARG = IMG_CHAO.get_width()
    IMG = IMG_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARG

    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED

        if self.x1 + self.LARG <= 0:
            self.x1 = self.x2 + self.LARG
        if self.x2 + self.LARG <= 0:
            self.x2 = self.x1 + self.LARG

    def draw(self, screen):
        screen.blit(self.IMG, (self.x1, self.y))
        screen.blit(self.IMG, (self.x2, self.y))

# Fuctions of the game system 😎


def gameOver(screen):
    psound(os.path.join("sounds", "gameover.ogg"), False)

    fonte = game.font.SysFont('arial', 60)
    texto_game_over = fonte.render("Game Over", True, (255, 0, 0))
    texto_retry = FONT.render("Retry", True, (255, 255, 255))

    # Button
    button_largura = 200
    button_altura = 60
    botao_x = (TELA_LARGURA - button_largura)//2
    botao_y = (TELA_LARGURA - button_altura)//2 + 50
    botao_rect = game.Rect(botao_x, botao_y, button_largura, button_altura)

    while True:
        screen.blit(IMG_BACK, (0, 0))
        screen.blit(texto_game_over,
                    ((TELA_LARGURA - texto_game_over.get_width())//2, 200))

        game.draw.rect(screen, (0, 100, 200), botao_rect)
        screen.blit(texto_retry, (
            botao_x, (button_largura - texto_retry.get_width()) // 2,
            botao_y, (button_altura - texto_retry.get_height()) // 2
        ))
        game.display.update()

        for event in game.event.get():
            if event.type == game.QUIT:
                game.quit()
                quit()
            if event.type == game.MOUSEBUTTONDOWN:
                if (botao_rect.collidepoint(event.pos)):
                    return True


def desenhar_tela(screen, birds, pipes, pontos, Ground):
    screen.blit(IMG_BACK, (0, 0))

    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)
    Ground.draw(screen)
    text = FONT.render(f'Pontuação {pontos}', 1, (255, 255, 255))
    text.blit(text, (TELA_LARGURA - 10 - text.get_width(), 10))

    game.display.update()


def main():
    psound(os.path.join("sounds", "overflow.ogg"), True)

    birds = [Bird(230, 350)]
    ground = Ground(730)
    pipes = [Pipe(700)]
    screen = game.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = game.time.Clock()

    # loopgame
    rodando = True
    while rodando:
        relogio.tick(30)
        # user interact
        for evento in game.event.get():
            if evento.type == game.QUIT:
                rodando = False
                game.quit()
                quit()
            if evento.type == game.KEYDOWN:
                if evento.key == game.K_SPACE:
                    for bird in birds:
                        bird.jump()
        for bird in birds:
            bird.move()
        ground.move()

        add_pipe = False
        removepipe = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.col(bird):
                    if gameOver(screen):
                        main()
                    else:
                        rodando = False
                        game.quit()
                        quit()
                if not pipe.passou and bird.x > pipe.x:
                    pipe.passou = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                removepipe.append(pipe)
        if add_pipe:
            pontos += 1
            pipes.append(Pipe(600))

        for pipe in removepipe:
            removepipe.remove(pipe)
        for i, bird in enumerate(birds):
            if (bird.y + bird.img.get_height() > ground.y or bird.y < 0):
                if gameOver(screen):
                    main()
                else:
                    rodando = False
                    game.quit()
                    quit()
        desenhar_tela(screen, birds, pipes, pontos, ground)


if __name__ == "__main__":
    main()
