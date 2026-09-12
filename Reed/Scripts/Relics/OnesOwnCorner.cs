using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Relics;

/// <summary>
/// 独属自己的一隅（OnesOwnCorner）—— 不常见遗物。
/// 受到未被格挡的伤害时，对自己施加等量层数的灼燃计数器。
/// </summary>
[RegisterRelic(typeof(ReedRelicPool))]
public sealed class OnesOwnCorner : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.png",
        IconOutlinePath: $"{Entry.ResPath}/images/relics/{GetType().Name}.png",
        BigIconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.png");

    public override bool ShouldReceiveCombatHooks => true;

    public override async Task AfterDamageReceived(PlayerChoiceContext choiceContext, Creature target, DamageResult result, ValueProp props, Creature dealer, CardModel cardSource)
    {
        if (target != Owner.Creature) return;
        if (result.UnblockedDamage <= 0) return;

        int scorchCounter = result.UnblockedDamage;
        await PowerCmd.Apply<ScorchCounter>(choiceContext, Owner.Creature, scorchCounter, Owner.Creature, null);
    }
}
