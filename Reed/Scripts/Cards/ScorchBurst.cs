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
/// 灼燃爆发（ScorchBurst）——罕见攻击牌。
/// 1费，造成6点伤害，消耗所有自身灼燃，每层额外造成3点伤害（升级后每层+2）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class ScorchBurst : ModCardTemplate
{
    private const int BaseEnergyCost = 1;
    private const CardType CardKind = CardType.Attack;
    private const CardRarity CardRarityValue = CardRarity.Uncommon;
    private const TargetType CardTarget = TargetType.AnyEnemy;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(6, ValueProp.Move),
        new CardsVar(3) // 每层灼燃额外伤害
    ];

    public ScorchBurst() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target);

        int scorchStacks = ReedCombatHelper.GetPowerAmount<ScorchCounter>(Owner.Creature);
        int bonusDamage = scorchStacks * DynamicVars.Cards.IntValue;
        int totalDamage = (int)DynamicVars.Damage.BaseValue + bonusDamage;

        await DamageCmd.Attack(totalDamage)
            .FromCard(this, cardPlay)
            .Targeting(cardPlay.Target)
            .Execute(choiceContext);

        if (scorchStacks > 0)
        {
            await ReedCombatHelper.RemoveAllPower<ScorchCounter>(Owner.Creature, choiceContext);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(2);
}
