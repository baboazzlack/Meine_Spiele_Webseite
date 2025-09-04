// static/js/games/simple_invaders_logic.js

function createPlayer(canvas) {
    return {
        x: canvas.width / 2 - 25, y: canvas.height - 40,
        width: 50, height: 20,
        color: '#00ffff', speed: 0,
        draw(ctx) { ctx.fillStyle = this.color; ctx.fillRect(this.x, this.y, this.width, this.height); },
        update() { 
            this.x += this.speed; 
            if (this.x < 0) this.x = 0; 
            if (this.x + this.width > canvas.width) this.x = canvas.width - this.width; 
        }
    };
}

function createProjectile(x, y, color, velocityY) {
    return { x, y, width: 4, height: 10, color, velocityY,
        draw(ctx) { ctx.fillStyle = this.color; ctx.fillRect(this.x, this.y, this.width, this.height); },
        update() { this.y += this.velocityY; }
    };
}

function createInvader(x, y) {
    return { x, y, width: 30, height: 20, color: '#ffff00',
        draw(ctx, gridX, gridY) { ctx.fillStyle = this.color; ctx.fillRect(this.x + gridX, this.y + gridY, this.width, this.height); }
    };
}

function createInvaderGrid() {
    const grid = {
        x: 0, y: 0, speedX: 1,
        invaders: []
    };
    const gridWidth = 10;
    for (let i = 0; i < gridWidth; i++) {
        for (let j = 0; j < 4; j++) {
            grid.invaders.push(createInvader(i * 40, j * 30 + 40));
        }
    }
    return grid;
}


// Dieser Block stellt sicher, dass der Code sowohl im Browser als auch in Jest funktioniert.
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { createPlayer, createProjectile, createInvader, createInvaderGrid };
}