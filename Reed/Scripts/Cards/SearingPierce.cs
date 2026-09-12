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
/// 灼穿（SearingPierce）——不常见攻击牌。1费，造成6点伤害（升级后+2点），目标每有1层灼燃额外造成3点伤害（升级后+2点）。目标获得灼燃免疫（不再受到灼燃伤害）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class SearingPierce : ModCardTemplate
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

    public SearingPierce() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target);

        int damage = (int)DynamicVars.Damage.BaseValue;
        int bonusPerScorch = DynamicVars.Cards.IntValue;
        int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(cardPlay.Target);
        damage += bonusPerScorch * scorchStacks;

        await DamageCmd.Attack(damage)
            .FromCard(this, cardPlay)
            .Targeting(cardPlay.Target)
            .Execute(choiceContext);

        // 削弱：目标获得灼燃免疫（不再受到灼燃伤害）
        await PowerCmd.Apply<ScorchImmunity>(choiceContext, cardPlay.Target, 1, Owner.Creature, null);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(2);
        DynamicVars.Cards.UpgradeValueBy(2);
    }
}
