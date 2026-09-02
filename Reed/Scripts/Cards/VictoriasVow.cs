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
/// 维多利亚誓约（VictoriasVow）——稀有技能牌。
/// 2费，每有一个带有灼燃的敌人，获得1点力量（升级后2点）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class VictoriasVow : ModCardTemplate
{
    private const int BaseEnergyCost = 2;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Rare;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(1) // 每个带有灼燃的敌人提供的力量值
    ];

    public VictoriasVow() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);
        int scorchEnemyCount = 0;
        foreach (var enemy in enemies)
        {
            if (ReedCombatHelper.HasPower<Scorch>(enemy))
            {
                scorchEnemyCount++;
            }
        }

        if (scorchEnemyCount > 0)
        {
            await PowerCmd.Apply<StrengthPower>(
                choiceContext,
                Owner.Creature,
                scorchEnemyCount * DynamicVars.Cards.IntValue,
                Owner.Creature,
                this);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(1);
}
