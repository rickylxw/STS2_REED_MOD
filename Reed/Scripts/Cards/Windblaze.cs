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
/// 风助火势（Windblaze）——稀有能力牌。
/// 2费，获得1层风助火势（升级后2层）。
/// 每个玩家回合结束时，所有敌人获得等量层数的灼燃。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class Windblaze : ModCardTemplate
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
        new CardsVar(1) // 每回合增长的灼燃层数
    ];

    public Windblaze() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<WindblazePower>(choiceContext, Owner.Creature, DynamicVars.Cards.IntValue, Owner.Creature, this);
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
