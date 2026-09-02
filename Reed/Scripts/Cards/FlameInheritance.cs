using System.Linq;
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
/// 薪火相传（FlameInheritance）——罕见技能牌�?/// 1费，将目标的所有灼燃转移到其他所有敌人身上�?/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class FlameInheritance : ModCardTemplate
{
    private const int BaseEnergyCost = 1;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Uncommon;
    private const TargetType CardTarget = TargetType.AnyEnemy;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars => [];

    public FlameInheritance() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target);

        int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(cardPlay.Target);

        if (scorchStacks > 0)
        {
            // 移除目标所有灼�?            await ReedCombatHelper.RemoveAllPower<Scorch>(cardPlay.Target, choiceContext);

            // 将灼燃转移到其他敌人
            var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);
            foreach (var enemy in enemies)
            {
                if (enemy != cardPlay.Target)
                {
                    await PowerCmd.Apply<Scorch>(choiceContext, enemy, scorchStacks, Owner.Creature, this);
                }
            }
        }
    }

    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}
