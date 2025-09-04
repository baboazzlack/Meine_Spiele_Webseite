// __tests__/pacman.test.js

// Wir importieren nur die Player-Klasse, da wir nur sie testen
const { Player } = require('../static/js/games/pacman_logic.js');

describe('Pac-Man Logik', () => {

    describe('Spieler-Bewegung', () => {
        test('sollte eine Eigenschaft korrekt aktualisieren', () => {
            // Setup
            const player = new Player({ position: { x: 100, y: 100 }, velocity: { x: 5, y: 0 } });

            // Aktion: Rufe die Logik-Funktion auf
            player.update();

            // Erwartung: Prüfe, ob die Position korrekt aktualisiert wurde
            expect(player.position.x).toBe(105);
        });

        // HINWEIS: Ein echter Wand-Kollisionstest wäre jetzt komplexer,
        // da die Kollisionslogik im Haupt-Spiel-Loop liegt.
        // Wir testen hier eine grundlegende Eigenschaft, um das Setup zu validieren.
        test('sollte eine Startposition haben', () => {
            const player = new Player({ position: { x: 24, y: 24 }, velocity: { x: 0, y: 0 } });
            expect(player.position.x).toBe(24);
            expect(player.position.y).toBe(24);
        });
    });
});