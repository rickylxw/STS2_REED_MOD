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
/// 火葬（Pyre）——稀有攻击牌。
/// 2费，造成8点伤害；若目标因此死亡，获得其灼燃层数×2的灰烬；未死亡则施加3层灼燃。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class Pyre : ModCardTemplate
{
    private const int BaseEnergyCost = 2;
    private const CardType CardKind = CardType.Attack;
    private const CardRarity CardRarityValue = CardRarity.Rare;
    private const TargetType CardTarget = TargetType.AnyEnemy;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(8, ValueProp.Move),
        new CardsVar(3) // 未死亡时施加的灼燃层数
    ];

    public Pyre() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target);

        // 先记录灼燃层数（死亡后能力会被移除）
        int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(cardPlay.Target);

        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .FromCard(this, cardPlay)
            .Targeting(cardPlay.Target)
            .Execute(choiceContext);

        if (!cardPlay.Target.IsAlive)
        {
            if (scorchStacks > 0)
            {
                await PowerCmd.Apply<Ash>(choiceContext, Owner.Creature, scorchStacks * 2, Owner.Creature, this);
            }
        }
        else
        {
            await PowerCmd.Apply<Scorch>(choiceContext, cardPlay.Target, DynamicVars.Cards.IntValue, Owner.Creature, this);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Damage.UpgradeValueBy(4);
}
