using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Cards;

/// <summary>
/// 烈焰洪流（FlameTorrent）——罕见技能牌。
/// 2费，先对所有敌人施加法术脆弱，层数等于其当前灼燃层数。
/// 然后对所有敌人施加灼燃，层数等于其当前法术脆弱层数。
/// 升级后 -1 费。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class FlameTorrent : ModCardTemplate
{
    private const int BaseEnergyCost = 2;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Rare;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars => [];

    public FlameTorrent() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);

        // 第一步：对所有敌人施加法术脆弱，层数 = 其灼燃层数
        foreach (var enemy in enemies)
        {
            int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(enemy);
            if (scorchStacks > 0)
            {
                await PowerCmd.Apply<SpellVulnerable>(choiceContext, enemy, scorchStacks, Owner.Creature, this);
            }
        }

        // 第二步：对所有敌人施加灼燃，层数 = 其法术脆弱层数
        foreach (var enemy in enemies)
        {
            int spellVulnStacks = ReedCombatHelper.GetPowerAmount<SpellVulnerable>(enemy);
            if (spellVulnStacks > 0)
            {
                await PowerCmd.Apply<Scorch>(choiceContext, enemy, spellVulnStacks, Owner.Creature, this);
            }
        }
    }

    protected override void OnUpgrade() => EnergyCost.UpgradeBy(-1);
}
