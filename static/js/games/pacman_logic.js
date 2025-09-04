// static/js/games/pacman_logic.js

const TILE_SIZE = 24;

class Boundary {
    constructor({ position }) { this.position = position; this.width = TILE_SIZE; this.height = TILE_SIZE; }
}

class Player {
    constructor({ position, velocity }) {
        this.position = position; this.velocity = velocity;
        this.radius = TILE_SIZE / 2 * 0.75;
        this.radians = 0.75;
        this.openRate = 0.12;
        this.rotation = 0;
        this.speed = 2.5;
    }

    draw(ctx) {
        ctx.save();
        ctx.translate(this.position.x, this.position.y);
        ctx.rotate(this.rotation);
        ctx.translate(-this.position.x, -this.position.y);
        ctx.beginPath();
        ctx.arc(this.position.x, this.position.y, this.radius, this.radians, Math.PI * 2 - this.radians);
        ctx.lineTo(this.position.x, this.position.y);
        ctx.fillStyle = 'yellow';
        ctx.shadowColor = 'yellow';
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.closePath();
        ctx.restore();
        ctx.shadowBlur = 0;
    }

    update() { // Nimmt keinen `ctx` mehr entgegen
        this.position.x += this.velocity.x;
        this.position.y += this.velocity.y;
        if (this.radians < 0 || this.radians > 0.75) {
            this.openRate = -this.openRate;
        }
        this.radians += this.openRate;
    }
}

class Ghost {
    constructor({ position, velocity, color = 'red', speed = 2 }) {
        this.position = position;
        this.velocity = velocity;
        this.radius = TILE_SIZE / 2 * 0.75;
        this.color = color;
        this.prevCollisions = [];
        this.speed = speed;
        this.isScared = false;
    }
    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.position.x, this.position.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.isScared ? '#6495ED' : this.color;
        ctx.shadowColor = this.isScared ? '#6495ED' : this.color;
        ctx.shadowBlur = 15;
        ctx.fill();
        ctx.closePath();
        ctx.shadowBlur = 0;
    }
    update() { // Nimmt keinen `ctx` mehr entgegen
        this.position.x += this.velocity.x;
        this.position.y += this.velocity.y;
    }
}

class Pellet {
    constructor({ position }) { this.position = position; this.radius = 3; }
    draw(ctx) { ctx.beginPath(); ctx.arc(this.position.x, this.position.y, this.radius, 0, Math.PI * 2); ctx.fillStyle = 'white'; ctx.fill(); ctx.closePath(); }
}

class PowerUp {
    constructor({ position }) { this.position = position; this.radius = 8; }
    draw(ctx, frameCounter) {
        ctx.beginPath();
        ctx.arc(this.position.x, this.position.y, this.radius * (Math.sin(frameCounter * 0.1) * 0.2 + 0.8), 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.shadowColor = 'white';
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.closePath();
        ctx.shadowBlur = 0;
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Boundary, Player, Ghost, Pellet, PowerUp, TILE_SIZE };
}