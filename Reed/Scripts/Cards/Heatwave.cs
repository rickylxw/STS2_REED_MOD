using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Cards;

/// <summary>
/// 热浪（Heatwave）——稀有攻击牌。
/// 1费，对所有敌人造成4点伤害，你的每1点力量额外造成1点伤害。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class Heatwave : ModCardTemplate
{
    private const int BaseEnergyCost = 1;
    private const CardType CardKind = CardType.Attack;
    private const CardRarity CardRarityValue = CardRarity.Rare;
    private const TargetType CardTarget = TargetType.AllEnemies;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(4, ValueProp.Move)
    ];

    public Heatwave() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int strength = Owner.Creature.GetPowerAmount<StrengthPower>();
        if (strength < 0) strength = 0;

        int totalDamage = (int)DynamicVars.Damage.BaseValue + strength;

        var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);
        foreach (var enemy in enemies)
        {
            await DamageCmd.Attack(totalDamage)
                .FromCard(this, cardPlay)
                .Targeting(enemy)
                .Execute(choiceContext);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(2);
}
