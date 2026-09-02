using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Cards;

/// <summary>
/// 焰旋（FlameWhirl）——罕见攻击牌。
/// 1费，对所有敌人造成5点伤害，有灼燃的额外造成5点伤害（升级后+3/+3）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class FlameWhirl : ModCardTemplate
{
    private const int BaseEnergyCost = 1;
    private const CardType CardKind = CardType.Attack;
    private const CardRarity CardRarityValue = CardRarity.Uncommon;
    private const TargetType CardTarget = TargetType.AllEnemies;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(5, ValueProp.Move),
        new CardsVar(5) // 灼燃额外伤害
    ];

    public FlameWhirl() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);
        foreach (var enemy in enemies)
        {
            int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(enemy);
            int totalDamage = (int)DynamicVars.Damage.BaseValue;
            if (scorchStacks > 0)
                totalDamage += DynamicVars.Cards.IntValue;

            var damage = new DamageVar(totalDamage, ValueProp.Move);
            await CreatureCmd.Damage(choiceContext, enemy, damage, this, cardPlay);
        }
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(3);
        DynamicVars.Cards.UpgradeValueBy(3);
    }
}
