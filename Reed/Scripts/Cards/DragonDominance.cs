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
/// 龙威（DragonDominance）——稀有能力牌。
/// 2费，获得1层龙威（升级后2层）。
/// 每回合开始时，若所有敌人都带有灼燃，获得等量层数的力量。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class DragonDominance : ModCardTemplate
{
    private const int BaseEnergyCost = 2;
    private const CardType CardKind = CardType.Power;
    private const CardRarity CardRarityValue = CardRarity.Rare;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(1) // 龙威层数
    ];

    public DragonDominance() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<DragonDominancePower>(choiceContext, Owner.Creature, DynamicVars.Cards.IntValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
