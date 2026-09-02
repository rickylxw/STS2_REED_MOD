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
/// 灼燃觉醒（ScorchAwakening）——不常见技能牌。
/// 1费，消耗所有自身灼燃，每层获得1点力量（升级后每层+1）。消耗。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class ScorchAwakening : ModCardTemplate
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
        new CardsVar(1) // 每层灼燃获得的力量
    ];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public ScorchAwakening() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int scorchStacks = ReedCombatHelper.GetPowerAmount<ScorchCounter>(Owner.Creature);

        if (scorchStacks > 0)
        {
            await ReedCombatHelper.RemoveAllPower<ScorchCounter>(Owner.Creature, choiceContext);
            int strengthGain = scorchStacks * DynamicVars.Cards.IntValue;
            await PowerCmd.Apply<StrengthPower>(choiceContext, Owner.Creature, strengthGain, Owner.Creature, this);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
