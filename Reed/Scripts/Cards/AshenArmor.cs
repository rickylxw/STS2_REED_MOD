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
/// 烬甲（AshenArmor）——普通技能牌。
/// 1费，获得5点格挡，若拥有灰烬，额外获得等同灰烬层数的格挡（升级后基础格挡+3）。
/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class AshenArmor : ModCardTemplate
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
        new BlockVar(5m, ValueProp.Move) // 基础格挡
    ];

    public override bool GainsBlock => true;

    public AshenArmor() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        int ashStacks = ReedCombatHelper.GetPowerAmount<Ash>(Owner.Creature);
        int blockAmount = ashStacks + (int)DynamicVars.Block.BaseValue;

        if (blockAmount > 0)
        {
            var block = new BlockVar((decimal)blockAmount, ValueProp.Move);
            await CreatureCmd.GainBlock(Owner.Creature, block, cardPlay);
        }
    }

    protected override void OnUpgrade() => DynamicVars.Block.UpgradeValueBy(3);
}
