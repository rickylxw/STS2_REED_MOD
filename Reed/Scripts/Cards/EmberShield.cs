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
/// 余烬护盾（EmberShield）——普通技能牌。
/// 1费，获得格挡，数值等于所有敌人中最高灼燃层数+3（升级后+6）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class EmberShield : ModCardTemplate
{
    private const int BaseEnergyCost = 1;
    private const CardType CardKind = CardType.Skill;
    private const CardRarity CardRarityValue = CardRarity.Common;
    private const TargetType CardTarget = TargetType.Self;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(3) // 基础格挡加成
    ];

    public override bool GainsBlock => true;

    public EmberShield() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);
        int maxScorch = 0;
        foreach (var enemy in enemies)
        {
            int scorch = ReedCombatHelper.GetPowerAmount<Scorch>(enemy);
            if (scorch > maxScorch) maxScorch = scorch;
        }

        int blockAmount = maxScorch + DynamicVars.Cards.IntValue;
        if (blockAmount > 0)
        {
            var block = new BlockVar((decimal)blockAmount, ValueProp.Move);
            await CreatureCmd.GainBlock(Owner.Creature, block, cardPlay);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Cards.UpgradeValueBy(3);
}
