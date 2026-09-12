using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Relics;

/// <summary>
/// 赠予红龙的花冠（CrownOfTheRedDragon）—— 罕见遗物。
/// 你对敌人施加灼燃时，额外施加1层法术脆弱。
/// </summary>
[RegisterRelic(typeof(ReedRelicPool))]
public sealed class CrownOfTheRedDragon : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Rare;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.png",
        IconOutlinePath: $"{Entry.ResPath}/images/relics/{GetType().Name}.png",
        BigIconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.png");

    public override bool ShouldReceiveCombatHooks => true;

    public override async Task AfterPowerAmountChanged(PlayerChoiceContext choiceContext, PowerModel power, decimal amount, Creature applier, CardModel cardSource)
    {
        // 仅当我（玩家）给敌人施加灼燃时触发
        if (applier != Owner.Creature) return;
        if (power.Target == Owner.Creature) return;
        if (power is not Scorch) return;

        await PowerCmd.Apply<SpellVulnerable>(choiceContext, power.Target, 1, Owner.Creature, null);
    }
}
