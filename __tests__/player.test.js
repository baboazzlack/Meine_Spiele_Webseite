// __tests__/player.test.js

const { createPlayer } = require('../static/js/games/simple_invaders_logic.js');

describe('Player Logic', () => {

    test('sollte sich nach rechts bewegen, wenn die Geschwindigkeit positiv ist', () => {
        const mockCanvas = { width: 800, height: 600 };
        const player = createPlayer(mockCanvas);
        player.x = 100;
        player.speed = 5;

        // Aktion: Rufe nur die Logik-Funktion auf, ohne Argumente.
        player.update();

        // Erwartung: Prüfe das Ergebnis der Logik.
        expect(player.x).toBe(105);
    });

    test('sollte am linken Rand stoppen', () => {
        const mockCanvas = { width: 800, height: 600 };
        const player = createPlayer(mockCanvas);
        player.x = 2;
        player.speed = -5;

        player.update();

        expect(player.x).toBe(0);
    });
});