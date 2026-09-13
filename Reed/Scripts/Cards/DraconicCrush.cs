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
/// 巨龙重压（DraconicCrush）——不常见攻击牌。
/// 3费，造成18点伤害，每层灼燃计数器额外造成3点伤害，然后消耗自身所有灼燃计数器。
/// 升级后基础24点。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class DraconicCrush : ModCardTemplate
{
    private const int BaseEnergyCost = 3;
    private const CardType CardKind = CardType.Attack;
    private const CardRarity CardRarityValue = CardRarity.Uncommon;
    private const TargetType CardTarget = TargetType.AnyEnemy;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(18, ValueProp.Move),
        new CardsVar(3) // 每层灼燃计数器的额外伤害
    ];

    public DraconicCrush() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target);

        int counterStacks = ReedCombatHelper.GetPowerAmount<ScorchCounter>(Owner.Creature);
        int totalDamage = (int)DynamicVars.Damage.BaseValue + counterStacks * DynamicVars.Cards.IntValue;

        await DamageCmd.Attack(totalDamage)
            .FromCard(this, cardPlay)
            .Targeting(cardPlay.Target)
            .Execute(choiceContext);

        if (counterStacks > 0)
        {
            await ReedCombatHelper.RemoveAllPower<ScorchCounter>(Owner.Creature, choiceContext);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(6);
}
