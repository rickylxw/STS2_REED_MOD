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
/// 余烬鳞甲（EmberScales）——不常见技能牌。
/// 1费，获得6点格挡；每有一名带灼燃的敌人，额外获得2点格挡（升级后基础+3）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class EmberScales : ModCardTemplate
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
        new BlockVar(6m, ValueProp.Move),
        new CardsVar(2) // 每名带灼燃敌人的额外格挡
    ];

    public override bool GainsBlock => true;

    public EmberScales() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int scorchedEnemies = 0;
        var enemies = ReedCombatHelper.GetEnemies(Owner.Creature);
        foreach (var enemy in enemies)
        {
            if (ReedCombatHelper.GetPowerAmount<Scorch>(enemy) > 0)
            {
                scorchedEnemies++;
            }
        }

        int totalBlock = (int)DynamicVars.Block.BaseValue + scorchedEnemies * DynamicVars.Cards.IntValue;
        var block = new BlockVar(totalBlock, ValueProp.Move);
        await CreatureCmd.GainBlock(Owner.Creature, block, cardPlay);
    }

    protected override void OnUpgrade() => DynamicVars.Block.UpgradeValueBy(3);
}
