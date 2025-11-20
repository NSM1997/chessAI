import sys
sys.path.insert(0, '.')
from backend.app.services.tactical_analysis import get_tactical_service
import chess, asyncio

async def test():
    s = get_tactical_service()
    positions = [
        ("Fork", "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP1QPPP/RNB1K2R b KQkq - 0 5"),
        ("Pin", "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 4"),
    ]
    
    for name, fen in positions:
        b = chess.Board(fen)
        a = await s.analyze_tactics(b, threshold=0.5, top_k=10)
        print(f"\n{name} (threshold=0.5):")
        if a['themes']:
            for t in a['themes']:
                print(f"  {t['theme']:<20} {t['confidence']:.1%}")
        else:
            print("  (No predictions)")

asyncio.run(test())
