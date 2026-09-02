using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Cards;

/// <summary>
/// 焚身（BurnAway）——罕见技能牌。
/// 1费，移除自身所有灼燃，每层回复1点生命（升级后2点）并获得1点力量。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class BurnAway : ModCardTemplate
{
    private const int BaseEnergyCost = 1;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Uncommon;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(1) // 每层灼燃回复的生命值
    ];

    public BurnAway() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int scorchStacks = ReedCombatHelper.GetPowerAmount<ScorchCounter>(Owner.Creature);

        if (scorchStacks > 0)
        {
            // 移除自身所有灼燃计数器
            await ReedCombatHelper.RemoveAllPower<ScorchCounter>(Owner.Creature, choiceContext);

            // 每层回复生命
            await ReedCombatHelper.Heal(
                Owner.Creature,
                scorchStacks * DynamicVars.Cards.IntValue,
                choiceContext);

            // 每层获得力量
            await PowerCmd.Apply<StrengthPower>(choiceContext, Owner.Creature, scorchStacks, Owner.Creature, this);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
