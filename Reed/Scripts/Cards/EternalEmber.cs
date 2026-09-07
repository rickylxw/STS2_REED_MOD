using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Character;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Cards;

/// <summary>
/// 永恒余烬（Eternal Ember）——苇草的先古卡。
/// 通过达弗的薄污之书获得。
/// 3费，获得1层永恒余烬。
/// 每回合开始时，对所有敌人施加3层灼燃，并获得等于所有敌人灼燃总层数的格挡。
/// </summary>
// [RegisterCard] removed for Dusty Tome only
[RegisterDustyTomeCard(typeof(ReedCharacter))]
public sealed class EternalEmber : ModCardTemplate
    {
        protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
    private const int BaseEnergyCost = 3;
    private const CardType CardKind = CardType.Power;
    private const CardRarity CardRarityValue = CardRarity.Rare;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = false;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    public override CardVisualStyle CustomVisualStyle => CardVisualStyle.Ancient;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(1)
    ];

    public EternalEmber() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<EternalEmberPower>(choiceContext, Owner.Creature, DynamicVars.Cards.IntValue, Owner.Creature, this);
    }
}
