using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Character;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Relics;

/// <summary>
/// 鳞火护符（ScaleFlameCharm）。
/// 每场战斗中第一次受到伤害时，对攻击者施加3层灼燃。
/// </summary>
[RegisterRelic(typeof(ReedRelicPool))]
public sealed class ScaleFlameCharm : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Common;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg",
        IconOutlinePath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    private bool _triggeredThisCombat;

    public override Task BeforeCombatStart()
    {
        _triggeredThisCombat = false;
        return Task.CompletedTask;
    }

    public override async Task AfterDamageReceived(PlayerChoiceContext choiceContext, Creature target, DamageResult result, ValueProp props, Creature dealer, CardModel cardSource)
    {
        if (_triggeredThisCombat) return;
        if (target != Owner.Creature) return;
        if (result.UnblockedDamage <= 0) return;
        if (dealer == null) return;

        _triggeredThisCombat = true;
        await PowerCmd.Apply<Scorch>(choiceContext, dealer, 3, Owner.Creature, null);
    }
}
