using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Character;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Relics;

/// <summary>
/// 灰烬核心（AshenCore）——初始遗物。
/// 战斗开始时获得3层灰烬；每次消耗任何卡牌时，获得1层灰烬。
/// </summary>
[RegisterRelic(typeof(ReedRelicPool))]
[RegisterCharacterStarterRelic(typeof(ReedCharacter))]
public sealed class AshenCore : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Common;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg",
        IconOutlinePath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    private bool _gaveStartAshThisCombat;

    public override Task BeforeCombatStart()
    {
        _gaveStartAshThisCombat = false;
        return Task.CompletedTask;
    }

    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        if (_gaveStartAshThisCombat) return;
        _gaveStartAshThisCombat = true;
        await PowerCmd.Apply<Ash>(choiceContext, Owner.Creature, 3, Owner.Creature, null);
    }

    public override async Task AfterCardExhausted(PlayerChoiceContext choiceContext, CardModel card, bool causedByEthereal)
    {
        await PowerCmd.Apply<Ash>(choiceContext, Owner.Creature, 1, Owner.Creature, null);
    }
}
