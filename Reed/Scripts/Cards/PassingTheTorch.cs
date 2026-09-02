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
/// 薪火相传（PassingTheTorch）——罕见攻击牌。
/// 2费，造成等于目标灼燃层数3倍的伤害，然后移除目标所有灼燃。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class PassingTheTorch : ModCardTemplate
{
    private const int BaseEnergyCost = 2;
    private const CardType CardKind = CardType.Attack;
    private const CardRarity CardRarityValue = CardRarity.Uncommon;
    private const TargetType CardTarget = TargetType.AnyEnemy;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(3) // 灼燃伤害倍率
    ];

    public PassingTheTorch() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target);

        int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(cardPlay.Target);
        int multiplier = DynamicVars.Cards.IntValue;
        int damage = scorchStacks * multiplier;

        if (damage > 0)
        {
            await DamageCmd.Attack(damage)
                .FromCard(this, cardPlay)
                .Targeting(cardPlay.Target)
                .Execute(choiceContext);
        }

        // 移除目标所有灼燃（施加负值）
        if (scorchStacks > 0)
        {
            await PowerCmd.Apply<Scorch>(choiceContext, cardPlay.Target, -scorchStacks, Owner.Creature, this);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
