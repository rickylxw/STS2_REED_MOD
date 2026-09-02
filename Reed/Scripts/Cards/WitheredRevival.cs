using System.Linq;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Cards;

/// <summary>
/// 枯草逢春（WitheredRevival）——罕见技能牌。
/// 1费，消耗手牌中的一张牌，获得1层灰烬，抽1张牌（升级后2张）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class WitheredRevival : ModCardTemplate
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
        new CardsVar(1) // 抽牌数
    ];

    public WitheredRevival() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 简化为消耗手牌中第一张非本卡
        var handCards = ReedCombatHelper.GetHandCards(Owner);
        CardModel? toExhaust = handCards.FirstOrDefault(c => !ReferenceEquals(c, this));

        if (toExhaust != null)
        {
            await ReedCombatHelper.ExhaustCard(toExhaust, choiceContext);
        }

        // 抽牌
        await CardPileCmd.Draw(choiceContext, DynamicVars.Cards.IntValue, Owner);
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
