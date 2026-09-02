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
/// 灰烬引燃（AshIgnition）——不常见技能牌。
/// 1费，将所有灰烬转化为自身灼燃（每层灰烬→1层灼燃，升级后每层+1）。消耗。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class AshIgnition : ModCardTemplate
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
        new CardsVar(1) // 每层灰烬转化的灼燃层数
    ];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public AshIgnition() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int ashStacks = ReedCombatHelper.GetPowerAmount<Ash>(Owner.Creature);

        if (ashStacks > 0)
        {
            await ReedCombatHelper.RemoveAllPower<Ash>(Owner.Creature, choiceContext);
            int scorchAmount = ashStacks * DynamicVars.Cards.IntValue;
            await PowerCmd.Apply<ScorchCounter>(choiceContext, Owner.Creature, scorchAmount, Owner.Creature, this);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
