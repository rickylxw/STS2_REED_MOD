using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Cards;

/// <summary>
/// 燃烬之眼（EmberEye）——普通技能牌。
/// 0费，抽2张牌，若抽到的牌中有灼燃相关卡（非基础打击/防御），失去1生命（升级后抽3张）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class EmberEye : ModCardTemplate
{
    private const int BaseEnergyCost = 0;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Common;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(2) // 抽牌数
    ];

    public EmberEye() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 记录抽牌前的手牌
        var handBefore = ReedCombatHelper.GetHandCards(Owner).ToList();

        await CardPileCmd.Draw(choiceContext, DynamicVars.Cards.IntValue, Owner);

        // 检查新抽到的牌中是否有非基础牌
        var handAfter = ReedCombatHelper.GetHandCards(Owner).ToList();
        bool drewScorchRelated = false;
        foreach (var card in handAfter)
        {
            if (!handBefore.Any(c => ReferenceEquals(c, card)) && !card.IsBasicStrikeOrDefend)
            {
                drewScorchRelated = true;
                break;
            }
        }

        if (drewScorchRelated)
        {
            var damage = new DamageVar(1, ValueProp.Unpowered | ValueProp.Unblockable);
            await CreatureCmd.Damage(choiceContext, Owner.Creature, damage, null, cardPlay);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
