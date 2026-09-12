using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 烬火余韵（EmberAfterglowPower）——能力。
/// 每当一张牌被消耗时，抽1张牌，每回合最多抽 Amount 次。
/// </summary>
[RegisterPower]
public sealed class EmberAfterglowPower : ModPowerTemplate
{
    private int _drawnThisTurn;
    private Player? _player;

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        _player = player;
        _drawnThisTurn = 0;
    }

    public override async Task AfterCardExhausted(PlayerChoiceContext choiceContext, CardModel card, bool causedByEthereal)
    {
        if (Amount <= 0) return;
        if (_drawnThisTurn >= Amount) return;
        if (_player is null) return;

        _drawnThisTurn++;
        await CardPileCmd.Draw(choiceContext, 1, _player);
    }
}
