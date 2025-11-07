#!/usr/bin/env python3
"""
Generate natural, coach-like chess explanations
"""

import json
import random

# Natural, conversational explanation templates that sound like a coach
NATURAL_EXPLANATIONS = {
    "opening": {
        "e4": [
            "Start with e4! This is the king's pawn opening - you're claiming space in the center right away and giving your bishop and queen breathing room.",
            "e4 is my favorite first move. You're taking control of the center and letting your pieces come out naturally.",
            "Push that e-pawn two squares! You're fighting for the center and opening up diagonals for your queen and bishop.",
            "Let's go with e4 here. Classic and strong - you grab central space and free up your pieces.",
        ],
        "Nf3": [
            "Bring your knight out to f3. This develops a piece, puts pressure on the center, and keeps your options flexible.",
            "Nf3 is a great developing move. You're controlling key central squares without committing your pawns yet.",
            "Get that knight into the game! Nf3 attacks the center and prepares you to castle soon.",
            "Move your knight to f3. It's developing with purpose - controlling e5 and d4 while preparing to castle.",
        ],
        "d4": [
            "d4 is the queen's pawn opening. You're staking your claim in the center and opening lines for your pieces.",
            "Push d4 to control the center. This gives you a solid foundation to build your position.",
            "Start with d4! You're fighting for central control right from move one.",
        ],
        "Nf6": [
            "Respond with Nf6. You're developing while immediately challenging their central pawn.",
            "Bring your knight to f6. This attacks e4 and develops a piece at the same time - efficient!",
            "Nf6 is the right response. You're not letting them dominate the center for free.",
        ],
        "c5": [
            "c5 - the Sicilian Defense! You're fighting for control on the queenside and creating an asymmetric position.",
            "Play c5 here. This is the most ambitious response, immediately challenging white's center.",
            "Go with c5! You're saying 'I want to win' - creating imbalance from the start.",
        ],
        "Bc4": [
            "Develop your bishop to c4. It's aiming right at f7, that weak spot near their king.",
            "Bc4 puts immediate pressure on f7 and develops a piece actively.",
            "Get your bishop out to c4. You're developing with a threat!",
        ],
        "O-O": [
            "Castle now! Get your king to safety and connect your rooks.",
            "Time to castle. Your king needs protection before the middle game heats up.",
            "O-O is the move. King safety first - move it to the corner and bring your rook into the game.",
        ],
    },
    "middlegame": {
        "O-O": [
            "Castle right now! Your king is too exposed in the center - get it safe before tactics start flying.",
            "You've developed enough pieces. Time to castle and secure your king.",
            "O-O! Never leave your king in the center when the game is heating up.",
        ],
        "Bg5": [
            "Bg5 pins that knight to the queen! This creates immediate problems for your opponent.",
            "Develop with purpose - Bg5 pins the knight and puts pressure on their position.",
            "Bg5 is strong here. You're pinning the knight and making them uncomfortable.",
        ],
        "d4": [
            "Push d4 and open up the position! You want to break through in the center.",
            "d4 strikes at the heart of their position. This pawn break is critical.",
            "Time for d4! You're challenging their center and opening lines for your pieces.",
        ],
        "Qd2": [
            "Bring your queen to d2. This prepares to castle queenside and connects your rooks.",
            "Qd2 is flexible. You're keeping options open while improving your queen's position.",
        ],
        "Rad1": [
            "Activate your rook with Rad1! Put it on the open file where it can create threats.",
            "Rad1 brings another piece into the attack. Rooks love open files!",
            "Get your rook to d1 - it's going to be powerful on this open file.",
        ],
        "Bxf6": [
            "Take on f6! You're damaging their pawn structure and getting rid of a key defender.",
            "Bxf6 trades pieces but ruins their pawns. That's a good trade for you.",
            "Capture on f6. When they recapture, they'll have doubled pawns - a long-term weakness.",
        ],
        "Nd5": [
            "Jump to d5! This is a strong central outpost for your knight.",
            "Nd5 is powerful - your knight is dominating from this central square.",
            "Plant your knight on d5. It's controlling so many important squares from there!",
        ],
        "f4": [
            "Push f4! You're launching a kingside attack - be aggressive here.",
            "f4 starts your attack on their king. Time to create threats!",
            "Go f4! This pawn storm is going to open lines toward their king.",
        ],
    },
    "endgame": {
        "Kf3": [
            "In the endgame, your king is a fighting piece! Bring it forward with Kf3.",
            "Activate your king - Kf3 gets it into the game. Kings become powerful in the endgame.",
            "Kf3 is the move. In endgames, the king must be active!",
        ],
        "Kd3": [
            "Centralize your king with Kd3. In the endgame, the king should be in the center of the action.",
            "Kd3 activates your king. Remember: kings are strong in endgames!",
        ],
        "Ke3": [
            "Ke3 brings your king closer to the center. Every tempo matters in this endgame!",
            "Step forward with Ke3. Your king needs to support your pawns.",
        ],
        "a4": [
            "Push a4! Create a passed pawn - these are gold in the endgame.",
            "a4 starts advancing your pawn. Passed pawns must be pushed!",
            "a4 is key. You're creating threats that will tie down their pieces.",
        ],
        "Rxd8": [
            "Trade rooks with Rxd8. Simplification is good when you're ahead in material.",
            "Rxd8 simplifies the position. With your extra material, trading pieces makes winning easier.",
        ],
        "Kxf5": [
            "Capture with your king! Kxf5 grabs the pawn and improves your position.",
            "Kxf5 wins material. In the endgame, every pawn counts!",
        ],
    },
    "tactical": {
        "fork": "This move creates a fork - you're attacking two pieces at once! They can only save one.",
        "pin": "Beautiful pin! That piece is stuck defending something more valuable.",
        "skewer": "This is a skewer - they have to move their valuable piece and lose the one behind it.",
        "discovered_attack": "When you move this piece, you're uncovering an attack from another piece. Double threat!",
        "check": "Check! Force them to respond to your threat first.",
        "mate_threat": "You're threatening checkmate! They have to deal with this immediately.",
        "deflection": "This forces their defender away from what it's protecting. Classic deflection tactic!",
        "removal_of_defender": "Remove that defender! Once it's gone, you can capture what it was protecting.",
    }
}

def generate_natural_training_data():
    """Generate natural, coach-like training data"""
    
    training_data = []
    
    # Opening positions
    opening_positions = [
        {
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "move": "e2e4",
            "move_san": "e4",
            "type": "opening",
            "key": "e4"
        },
        {
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "move": "g1f3",
            "move_san": "Nf3",
            "type": "opening",
            "key": "Nf3"
        },
        {
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "move": "d2d4",
            "move_san": "d4",
            "type": "opening",
            "key": "d4"
        },
        {
            "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
            "move": "g8f6",
            "move_san": "Nf6",
            "type": "opening",
            "key": "Nf6"
        },
        {
            "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
            "move": "c7c5",
            "move_san": "c5",
            "type": "opening",
            "key": "c5"
        },
        {
            "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
            "move": "f1c4",
            "move_san": "Bc4",
            "type": "opening",
            "key": "Bc4"
        },
        {
            "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4",
            "move": "e1g1",
            "move_san": "O-O",
            "type": "opening",
            "key": "O-O"
        },
    ]
    
    # Middlegame positions
    middlegame_positions = [
        {
            "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4",
            "move": "e1g1",
            "move_san": "O-O",
            "type": "middlegame",
            "key": "O-O"
        },
        {
            "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4",
            "move": "c1g5",
            "move_san": "Bg5",
            "type": "middlegame",
            "key": "Bg5"
        },
        {
            "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4",
            "move": "d3d4",
            "move_san": "d4",
            "type": "middlegame",
            "key": "d4"
        },
        {
            "fen": "rnbqk2r/ppp2ppp/3b1n2/3p4/3P4/3B1N2/PPP2PPP/RNBQK2R w KQkq - 4 6",
            "move": "d1d2",
            "move_san": "Qd2",
            "type": "middlegame",
            "key": "Qd2"
        },
        {
            "fen": "r2qkb1r/ppp2ppp/2n2n2/3p4/3P4/3B1N2/PPP1QPPP/RNB1K2R w KQkq - 2 8",
            "move": "a1d1",
            "move_san": "Rad1",
            "type": "middlegame",
            "key": "Rad1"
        },
        {
            "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/3PP3/2N2N2/PPP2PPP/R1BQKB1R b KQkq d3 0 4",
            "move": "c1f6",
            "move_san": "Bxf6",
            "type": "middlegame",
            "key": "Bxf6"
        },
        {
            "fen": "r1bqkb1r/ppp2ppp/2np1n2/4p3/4P3/2NP1N2/PPP2PPP/R1BQKB1R w KQkq - 0 5",
            "move": "f3d5",
            "move_san": "Nd5",
            "type": "middlegame",
            "key": "Nd5"
        },
        {
            "fen": "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 6 8",
            "move": "f2f4",
            "move_san": "f4",
            "type": "middlegame",
            "key": "f4"
        },
    ]
    
    # Endgame positions
    endgame_positions = [
        {
            "fen": "8/8/8/8/8/8/4K3/4k3 w - - 0 1",
            "move": "e2f3",
            "move_san": "Kf3",
            "type": "endgame",
            "key": "Kf3"
        },
        {
            "fen": "8/8/8/8/8/8/4K3/4k3 w - - 0 1",
            "move": "e2d3",
            "move_san": "Kd3",
            "type": "endgame",
            "key": "Kd3"
        },
        {
            "fen": "8/8/8/8/8/8/4K3/4k3 w - - 0 1",
            "move": "e2e3",
            "move_san": "Ke3",
            "type": "endgame",
            "key": "Ke3"
        },
        {
            "fen": "8/8/4k3/8/P7/8/8/4K3 w - - 0 1",
            "move": "a4a5",
            "move_san": "a4",
            "type": "endgame",
            "key": "a4"
        },
        {
            "fen": "3r4/8/4k3/8/8/4K3/3R4/8 w - - 0 1",
            "move": "d2d8",
            "move_san": "Rxd8",
            "type": "endgame",
            "key": "Rxd8"
        },
        {
            "fen": "8/8/4k3/5p2/4K3/8/8/8 w - - 0 1",
            "move": "e4f5",
            "move_san": "Kxf5",
            "type": "endgame",
            "key": "Kxf5"
        },
    ]
    
    # Generate multiple variations for each position
    all_positions = opening_positions + middlegame_positions + endgame_positions
    
    # Duplicate the dataset multiple times with slight variations to expand size
    for repeat in range(15):  # Repeat dataset 15 times
        for pos in all_positions:
            position_type = pos["type"]
            move_key = pos["key"]
            
            # Get explanations for this move type
            if position_type in NATURAL_EXPLANATIONS and move_key in NATURAL_EXPLANATIONS[position_type]:
                explanations = NATURAL_EXPLANATIONS[position_type][move_key]
                
                # Use each explanation variation
                for explanation in explanations:
                    input_text = f"Chess position: {pos['fen']} | Move: {pos['move_san']} ({pos['move']}) | Type: {position_type}"
                    
                    training_data.append({
                        "input": input_text,
                        "output": explanation,
                        "metadata": {
                            "fen": pos["fen"],
                            "move": pos["move"],
                            "move_san": pos["move_san"],
                            "position_type": position_type
                        }
                    })
    
    # Add some tactical examples with varied explanations
    tactical_examples = [
        ("Nxe5", "fork", "opening"),
        ("Qh5", "mate_threat", "middlegame"),
        ("Bb5", "pin", "middlegame"),
        ("Re8", "check", "middlegame"),
        ("Nd5", "fork", "middlegame"),
        ("Bxf7", "removal_of_defender", "middlegame"),
    ]
    
    for repeat in range(20):  # Repeat tactical examples 20 times
        for move, tactic, phase in tactical_examples:
            base_explanation = NATURAL_EXPLANATIONS["tactical"][tactic]
            
            # Add variations
            variations = [
                f"{base_explanation}",
                f"Here's the key: {base_explanation.lower()}",
                f"Look at this! {base_explanation}",
            ]
            
            for i, explanation in enumerate(variations):
                input_text = f"Chess position: tactical_{tactic}_{i} | Move: {move} | Type: {phase} | Tactic: {tactic}"
                
                training_data.append({
                    "input": input_text,
                    "output": explanation,
                    "metadata": {
                        "fen": f"tactical_{tactic}",
                        "move": move.lower(),
                        "move_san": move,
                        "position_type": phase,
                        "tactic": tactic
                    }
                })
    
    return training_data

def main():
    print("Generating natural, coach-like chess explanations...")
    
    training_data = generate_natural_training_data()
    
    print(f"Generated {len(training_data)} training examples")
    
    # Save to file
    output_file = "data/chess_explanations_natural.json"
    with open(output_file, 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"Saved to {output_file}")
    
    # Show some examples
    print("\n" + "="*80)
    print("Sample explanations:")
    print("="*80)
    for i, example in enumerate(random.sample(training_data, min(5, len(training_data)))):
        print(f"\n{i+1}. Input: {example['input'][:70]}...")
        print(f"   Output: {example['output']}")

if __name__ == "__main__":
    main()
