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
/// 鐏肩┛锛圫earingPierce锛夆€斺�?涓嶅父瑙佹敾鍑荤墝銆?/// 1璐癸紝閫犳垚6鐐逛激瀹筹紙鍗囩骇�?鐐癸級锛岀洰鏍囨瘡�?灞傜伡鐕冮澶栭€犳�?鐐逛激瀹筹紙鍗囩骇�?鐐癸級銆?/// </summary>
[RegisterCard(typeof(ReedCardPool))]
public sealed class SearingPierce : ModCardTemplate
{
    private const int BaseEnergyCost = 1;
    private const CardType CardKind = CardType.Attack;
    private const CardRarity CardRarityValue = CardRarity.Uncommon;
    private const TargetType CardTarget = TargetType.AnyEnemy;
    private const bool ShowInCardLibrary = true;

    public override CardAssetProfile AssetProfile => new(
        PortraitPath: $"{Entry.ResPath}/images/cards/{GetType().Name}.svg");

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new DamageVar(6, ValueProp.Move),
        new CardsVar(3) // 姣忓眰鐏肩噧棰濆浼ゅ
    ];

    public SearingPierce() : base(BaseEnergyCost, CardKind, CardRarityValue, CardTarget, ShowInCardLibrary) { }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target);

        int damage = (int)DynamicVars.Damage.BaseValue;
        int bonusPerScorch = DynamicVars.Cards.IntValue;
        int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(cardPlay.Target);
        damage += bonusPerScorch * scorchStacks;

        await DamageCmd.Attack(damage)
            .FromCard(this, cardPlay)
            .Targeting(cardPlay.Target)
            .Execute(choiceContext);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(2);
        DynamicVars.Cards.UpgradeValueBy(2);
    }
}

