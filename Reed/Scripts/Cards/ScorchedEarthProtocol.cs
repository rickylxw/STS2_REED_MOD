using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Cards;

/// <summary>
/// 焦土协议（ScorchedEarthProtocol）——罕见技能牌。
/// 0费，将手牌中所有非攻击非技能牌消耗掉，每张提供1点能量（升级后每张2点能量）。消耗。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class ScorchedEarthProtocol : ModCardTemplate
{
    private const int BaseEnergyCost = 0;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Uncommon;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(1) // 每张牌提供的能量
    ];

    public override IEnumerable<CardKeyword> CanonicalKeywords => [CardKeyword.Exhaust];

    public ScorchedEarthProtocol() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var handCards = ReedCombatHelper.GetHandCards(Owner).ToList();
        int exhaustedCount = 0;

        foreach (var card in handCards)
        {
            if (card.Type != CardType.Attack && card.Type != CardType.Skill)
            {
                await ReedCombatHelper.ExhaustCard(card, choiceContext);
                exhaustedCount++;
            }
        }

        if (exhaustedCount > 0)
        {
            await PlayerCmd.GainEnergy((decimal)(exhaustedCount * DynamicVars.Cards.IntValue), Owner);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
