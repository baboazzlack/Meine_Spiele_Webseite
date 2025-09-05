document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elemente ---
    const canvas = document.getElementById('asteroidsCanvas');
    const ctx = canvas.getContext('2d');
    const scoreEl = document.getElementById('score');
    const livesEl = document.getElementById('lives');
    const difficultySelect = document.getElementById('difficulty');
    const startBtn = document.getElementById('startGameBtn');
    const modal = document.getElementById('gameOverModal');
    const finalScoreEl = document.getElementById('finalScore');
    const playerNameInput = document.getElementById('playerNameInput');
    const saveScoreBtn = document.getElementById('saveScoreBtn');
    const restartGameBtn = document.getElementById('restartGameBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    
    // Mobile Controls
    const rotLeftBtn = document.getElementById('btn-rot-left');
    const rotRightBtn = document.getElementById('btn-rot-right');
    const thrustBtn = document.getElementById('btn-thrust');
    const fireBtn = document.getElementById('btn-fire');

    // --- Spiel-Konstanten ---
    const SHIP_SIZE = 30;
    const SHIP_THRUST = 0.1;
    const SHIP_TURN_SPEED = 0.1;
    const FRICTION = 0.99;
    const BULLET_SPEED = 7;
    const BULLET_MAX = 5;
    const ASTEROID_NUM = 3;
    const ASTEROID_SPEED = 1;
    const ASTEROID_SIZE = 100;
    const ASTEROID_VERTICES = 10;
    const ASTEROID_JAG = 0.4;
    const SHIP_INVINCIBILITY_DUR = 3; // seconds
    const SHIP_BLINK_DUR = 0.1; // seconds
    const EXPLOSION_PARTICLE_NUM = 30;
    const PARTICLE_LIFESPAN = 60; // frames
    const PARTICLE_SPEED_MULTIPLIER = 2;

    // --- Spiel-Variablen ---
    let ship, asteroids, score, lives, level, gameLoopId, gameActive;
    let particles = [];

    // --- Game Objects ---
    class Ship {
        constructor() {
            this.x = canvas.width / 2;
            this.y = canvas.height / 2;
            this.r = SHIP_SIZE / 2;
            this.a = Math.PI / 2; // Angle in radians (pointing up)
            this.rot = 0;
            this.thrusting = false;
            this.vel = { x: 0, y: 0 };
            this.bullets = [];
            this.blinkTime = 0;
            this.blinkNum = Math.ceil(SHIP_INVINCIBILITY_DUR * 60 / (SHIP_BLINK_DUR * 60)); // frames
            this.exploding = false; // Neu für Explosionszustand
        }

        update() {
            if (this.exploding) return;

            // Blink
            if (this.blinkNum > 0) {
                this.blinkTime++;
                if(this.blinkTime % Math.ceil(SHIP_BLINK_DUR * 60) === 0) {
                     this.blinkNum--;
                     this.blinkTime = 0; // Reset blinkTime for next blink phase
                }
            }

            // Thrust
            if (this.thrusting) {
                this.vel.x += SHIP_THRUST * Math.cos(this.a);
                this.vel.y -= SHIP_THRUST * Math.sin(this.a);
            }

            // Friction
            this.vel.x *= FRICTION;
            this.vel.y *= FRICTION;

            // Move ship
            this.x += this.vel.x;
            this.y += this.vel.y;

            // Rotate ship
            this.a += this.rot;

            // Handle screen wrapping
            if (this.x < 0 - this.r) this.x = canvas.width + this.r;
            if (this.x > canvas.width + this.r) this.x = 0 - this.r;
            if (this.y < 0 - this.r) this.y = canvas.height + this.r;
            if (this.y > canvas.height + this.r) this.y = 0 - this.r;
            
            // Bullets
            for (let i = this.bullets.length - 1; i >= 0; i--) {
                this.bullets[i].update();
                if (this.bullets[i].offscreen()) {
                    this.bullets.splice(i, 1);
                }
            }
        }

        draw() {
            if (this.exploding) return;

            if(this.blinkNum % 2 === 0) { // Blink effect
                ctx.strokeStyle = '#00ffff';
                ctx.lineWidth = SHIP_SIZE / 15;
                ctx.shadowColor = '#00ffff';
                ctx.shadowBlur = 10;
                ctx.beginPath();
                ctx.moveTo(
                    this.x + this.r * Math.cos(this.a),
                    this.y - this.r * Math.sin(this.a)
                );
                ctx.lineTo(
                    this.x - this.r * (Math.cos(this.a) + Math.sin(this.a)),
                    this.y + this.r * (Math.sin(this.a) - Math.cos(this.a))
                );
                ctx.lineTo(
                    this.x - this.r * (Math.cos(this.a) - Math.sin(this.a)),
                    this.y + this.r * (Math.sin(this.a) + Math.cos(this.a))
                );
                ctx.closePath();
                ctx.stroke();
                ctx.shadowBlur = 0; // Reset shadow
            }

            // Draw thrust
            if (this.thrusting && this.blinkNum % 2 === 0) {
                ctx.fillStyle = '#ff00ff';
                ctx.strokeStyle = '#ffff00';
                ctx.lineWidth = SHIP_SIZE / 20;
                ctx.shadowColor = '#ffff00';
                ctx.shadowBlur = 5;
                ctx.beginPath();
                ctx.moveTo( // Rear left
                    this.x - this.r * (Math.cos(this.a) + 0.5 * Math.sin(this.a)),
                    this.y + this.r * (Math.sin(this.a) - 0.5 * Math.cos(this.a))
                );
                ctx.lineTo( // Rear center behind ship
                    this.x - this.r * 1.5 * Math.cos(this.a),
                    this.y + this.r * 1.5 * Math.sin(this.a)
                );
                 ctx.lineTo( // Rear right
                    this.x - this.r * (Math.cos(this.a) - 0.5 * Math.sin(this.a)),
                    this.y + this.r * (Math.sin(this.a) + 0.5 * Math.cos(this.a))
                );
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
                ctx.shadowBlur = 0; // Reset shadow
            }

            this.bullets.forEach(b => b.draw());
        }

        shoot() {
            if (this.bullets.length < BULLET_MAX) {
                this.bullets.push(new Bullet(this.x, this.y, this.a, this.vel.x, this.vel.y)); // Ship's velocity added
            }
        }
        
        // Neu: Explosion des Schiffs
        explode() {
            this.exploding = true;
            for (let i = 0; i < EXPLOSION_PARTICLE_NUM; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * PARTICLE_SPEED_MULTIPLIER;
                particles.push(new Particle(this.x, this.y, speed * Math.cos(angle), speed * Math.sin(angle), '#ff00ff', PARTICLE_LIFESPAN));
            }
        }
    }

    class Bullet {
        constructor(x, y, a, shipVelX, shipVelY) { // Ship velocity added
            this.x = x + 4/3 * SHIP_SIZE/2 * Math.cos(a); // Start from ship nose
            this.y = y - 4/3 * SHIP_SIZE/2 * Math.sin(a);
            this.vel = {
                x: BULLET_SPEED * Math.cos(a) + shipVelX, // Add ship's velocity
                y: -BULLET_SPEED * Math.sin(a) + shipVelY // Add ship's velocity
            };
        }
        update() {
            this.x += this.vel.x;
            this.y += this.vel.y;
        }
        draw() {
            ctx.fillStyle = '#39ff14';
            ctx.shadowColor = '#39ff14';
            ctx.shadowBlur = 5;
            ctx.beginPath();
            ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }
        offscreen() {
            return this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height;
        }
    }

    class Asteroid {
        constructor(x, y, r) {
            this.x = x || Math.random() * canvas.width;
            this.y = y || Math.random() * canvas.height;
            this.r = r || ASTEROID_SIZE / 2;
            this.vel = {
                x: Math.random() * ASTEROID_SPEED * (Math.random() < 0.5 ? 1 : -1),
                y: Math.random() * ASTEROID_SPEED * (Math.random() < 0.5 ? 1 : -1)
            };
            this.a = 0;
            this.rot = (Math.random() - 0.5) * 0.02;
            this.vertices = [];
            for (let i = 0; i < ASTEROID_VERTICES; i++) {
                this.vertices.push(Math.random() * ASTEROID_JAG * 2 + 1 - ASTEROID_JAG);
            }
        }
        update() {
            this.x += this.vel.x;
            this.y += this.vel.y;
            this.a += this.rot;

            if (this.x < 0 - this.r) this.x = canvas.width + this.r;
            if (this.x > canvas.width + this.r) this.x = 0 - this.r;
            if (this.y < 0 - this.r) this.y = canvas.height + this.r;
            if (this.y > canvas.height + this.r) this.y = 0 - this.r;
        }
        draw() {
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.shadowColor = '#ffffff'; // Neon Glow
            ctx.shadowBlur = 8; // Neon Glow intensity
            ctx.beginPath();
            ctx.moveTo(
                this.x + this.r * this.vertices[0] * Math.cos(this.a),
                this.y + this.r * this.vertices[0] * Math.sin(this.a)
            );
            for (let i = 1; i < ASTEROID_VERTICES; i++) {
                ctx.lineTo(
                    this.x + this.r * this.vertices[i] * Math.cos(this.a + i * Math.PI * 2 / ASTEROID_VERTICES),
                    this.y + this.r * this.vertices[i] * Math.sin(this.a + i * Math.PI * 2 / ASTEROID_VERTICES)
                );
            }
            ctx.closePath();
            ctx.stroke();
            ctx.shadowBlur = 0; // Reset shadow
        }
        
        // Neu: Explosion des Asteroiden
        explode() {
            for (let i = 0; i < EXPLOSION_PARTICLE_NUM / 2; i++) { // Fewer particles for asteroids
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * PARTICLE_SPEED_MULTIPLIER;
                particles.push(new Particle(this.x, this.y, speed * Math.cos(angle), speed * Math.sin(angle), '#ffffff', PARTICLE_LIFESPAN / 2));
            }
        }
    }

    // Neu: Partikel-Klasse für Explosionen
    class Particle {
        constructor(x, y, vx, vy, color, lifespan) {
            this.x = x;
            this.y = y;
            this.vx = vx;
            this.vy = vy;
            this.color = color;
            this.lifespan = lifespan;
            this.originalLifespan = lifespan;
            this.size = Math.random() * 2 + 1;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.lifespan--;
            this.vx *= 0.98; // Friction for particles
            this.vy *= 0.98;
        }

        draw() {
            ctx.fillStyle = this.color;
            ctx.globalAlpha = this.lifespan / this.originalLifespan; // Fade out
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.globalAlpha = 1; // Reset alpha
        }
    }
    
    function distBetweenPoints(x1, y1, x2, y2) {
        return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    }

    function createAsteroids() {
        asteroids = [];
        const difficulty = difficultySelect.value;
        let numAsteroids = (level + (difficulty === 'easy' ? 1 : difficulty === 'medium' ? 2 : 4));
        for (let i = 0; i < numAsteroids; i++) {
            let a;
            do {
                a = new Asteroid();
            } while (distBetweenPoints(ship.x, ship.y, a.x, a.y) < ASTEROID_SIZE * 2 + ship.r);
            asteroids.push(a);
        }
    }

    function destroyAsteroid(index) {
        const a = asteroids[index];
        a.explode(); // Asteroid explodiert

        if (a.r > ASTEROID_SIZE / 4) {
            asteroids.push(new Asteroid(a.x, a.y, a.r / 2));
            asteroids.push(new Asteroid(a.x, a.y, a.r / 2));
            if (a.r > ASTEROID_SIZE / 2) score += 20; else score += 50;
        } else {
            score += 100;
        }
        asteroids.splice(index, 1);
        updateInfo();

        if (asteroids.length === 0) {
            level++;
            createAsteroids();
        }
    }
    
    function newLife() {
        lives--;
        ship.explode(); // Schiff explodiert
        updateInfo();

        if (lives === 0) {
            gameOver();
        } else {
            setTimeout(() => { // Warten, bis Explosion vorbei ist
                ship = new Ship(); // Neues Schiff
            }, PARTICLE_LIFESPAN / 60 * 1000); // Wait for particles to fade out
        }
    }

    function gameOver() {
        gameActive = false;
        startBtn.disabled = false;
        difficultySelect.disabled = false;
        finalScoreEl.textContent = score;
        if(score > 0) modal.style.display = 'flex';
    }

    function init() {
        ship = new Ship();
        level = 1;
        score = 0;
        lives = 3;
        particles = []; // Partikel für neues Spiel zurücksetzen
        createAsteroids();
        updateInfo();
    }
    
    function startGame() {
        gameActive = true;
        init();
        modal.style.display = 'none';
        startBtn.disabled = true;
        difficultySelect.disabled = true;
        if (gameLoopId) cancelAnimationFrame(gameLoopId);
        gameLoop();
    }

    function updateInfo() {
        scoreEl.textContent = score;
        livesEl.textContent = lives;
    }

    function gameLoop() {
        if (!gameActive) return;

        // Handle Controls
        ship.rot = (keys.ArrowLeft || mobileControls.rotLeft) ? SHIP_TURN_SPEED : (keys.ArrowRight || mobileControls.rotRight) ? -SHIP_TURN_SPEED : 0;
        ship.thrusting = keys.ArrowUp || mobileControls.thrust;
        if(keys.Space) { shoot(); keys.Space = false; }
        
        // Background
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Update & Draw Ship
        ship.update();
        ship.draw();
        
        // Update & Draw Asteroids
        asteroids.forEach(a => { a.update(); a.draw(); });

        // Update & Draw Particles
        for (let i = particles.length - 1; i >= 0; i--) {
            particles[i].update();
            particles[i].draw();
            if (particles[i].lifespan <= 0) {
                particles.splice(i, 1);
            }
        }

        // Collisions
        for (let i = asteroids.length - 1; i >= 0; i--) {
            // Skip collision check if ship is exploding
            if (!ship.exploding) {
                // Ship collision
                if (ship.blinkNum <= 0 && distBetweenPoints(ship.x, ship.y, asteroids[i].x, asteroids[i].y) < ship.r + asteroids[i].r) {
                    newLife();
                    destroyAsteroid(i); // Asteroid, der das Schiff getroffen hat, wird auch zerstört
                    // Wichtig: Wir brechen hier nicht ab, um weitere Asteroiden zu verarbeiten, aber das Schiff ist jetzt in der Explosionsphase.
                }
            }

            // Bullet collision with Asteroid
            for (let j = ship.bullets.length - 1; j >= 0; j--) {
                if (distBetweenPoints(ship.bullets[j].x, ship.bullets[j].y, asteroids[i].x, asteroids[i].r) < asteroids[i].r) {
                    ship.bullets.splice(j, 1);
                    destroyAsteroid(i);
                    // Nach Zerstörung des Asteroiden muss die innere Schleife neu starten, da sich das Asteroiden-Array geändert haben könnte.
                    // Das `break` hier ist ok, da eine Kugel nur einen Asteroiden treffen kann.
                    break; 
                }
            }
        }
        
        gameLoopId = requestAnimationFrame(gameLoop);
    }

    // --- Controls Handling ---
    const keys = {};
    const mobileControls = { rotLeft: false, rotRight: false, thrust: false };
    
    function shoot() {
        if (gameActive && !ship.exploding) ship.shoot();
    }
    
    document.addEventListener('keydown', e => {
        if(['ArrowUp', 'ArrowLeft', 'ArrowRight', 'Space'].includes(e.code)) e.preventDefault();
        keys[e.code] = true;
    });
    document.addEventListener('keyup', e => {
        keys[e.code] = false;
    });
    
    const touchHandler = (btn, state) => (e) => { e.preventDefault(); mobileControls[btn] = state; };
    rotLeftBtn.addEventListener('touchstart', touchHandler('rotLeft', true));
    rotLeftBtn.addEventListener('touchend', touchHandler('rotLeft', false));
    rotRightBtn.addEventListener('touchstart', touchHandler('rotRight', true));
    rotRightBtn.addEventListener('touchend', touchHandler('rotRight', false));
    thrustBtn.addEventListener('touchstart', touchHandler('thrust', true));
    thrustBtn.addEventListener('touchend', touchHandler('thrust', false));
    fireBtn.addEventListener('touchstart', (e) => { e.preventDefault(); shoot(); });

    // --- Event Listeners ---
    startBtn.addEventListener('click', startGame);
    restartGameBtn.addEventListener('click', startGame);
    closeModalBtn.addEventListener('click', () => modal.style.display = 'none');
    
    saveScoreBtn.addEventListener('click', () => {
        const playerName = playerNameInput.value.trim() || 'ANONYM';
        if (score > 0) {
             fetch("{% url 'games:save_score' %}", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': '{{ csrf_token }}' },
                body: JSON.stringify({ player_name: playerName, game: 'Asteroids', score: score })
            })
            .then(res => res.json())
            .then(data => { if(data.status === 'success') window.location.href = "{% url 'games:highscores' %}"; });
        }
    });
});