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
/// 焦土战术（ScorchedEarth）——罕见技能牌。
/// 2费，对所有敌人施加灼燃，层数等于所有敌人身上的灼燃总层数。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class ScorchedEarth : ModCardTemplate
{
    private const int BaseEnergyCost = 2;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Uncommon;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars => [];

    public ScorchedEarth() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // 计算所有敌人身上的灼燃总层数
        int totalScorch = ReedCombatHelper.GetAllEnemiesPowerTotal<Scorch>(Owner.Creature);

        if (totalScorch > 0)
        {
            var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);
            foreach (var enemy in enemies)
            {
                await PowerCmd.Apply<Scorch>(choiceContext, enemy, totalScorch, Owner.Creature, this);
            }
        }
    }

    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}
