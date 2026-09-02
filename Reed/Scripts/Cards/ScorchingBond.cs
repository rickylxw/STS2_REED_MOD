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
/// 灼燃之契（ScorchingBond）——联机专属不常见技能牌。
/// 1费，对所有敌人施加 {Cards} 层灼燃，每个友方获得 {Cards} 点力量。
/// 单人模式仅自身获得力量；联机模式所有玩家获得力量。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class ScorchingBond : ModCardTemplate
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
        new CardsVar(1) // 灼燃/力量层数
    ];

    public ScorchingBond() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);
        foreach (var enemy in enemies)
        {
            await PowerCmd.Apply<Scorch>(choiceContext, enemy, DynamicVars.Cards.IntValue, Owner.Creature, this);
        }
        var allies = ReedCombatHelper.GetAllies(Owner.Creature);
        foreach (var ally in allies)
        {
            await PowerCmd.Apply<StrengthPower>(choiceContext, ally, DynamicVars.Cards.IntValue, Owner.Creature, this);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
