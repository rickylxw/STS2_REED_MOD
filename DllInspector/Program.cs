using System;
using System.Reflection;
using System.Linq;
using System.Collections.Generic;

class Program
{
    static void Main()
    {
        string dataDir = @"E:\SteamLibrary\steamapps\common\Slay the Spire 2\data_sts2_windows_x86_64";
        string sts2Path = System.IO.Path.Combine(dataDir, "sts2.dll");
        string nugetPath = @"C:\Users\Administrator\.nuget\packages\sts2.ritsulib\0.5.18";
        string ritsuLibPath = System.IO.Path.Combine(nugetPath, "lib", "net9.0", "STS2-RitsuLib.dll");

        foreach (var dll in System.IO.Directory.GetFiles(dataDir, "*.dll"))
        {
            try { Assembly.LoadFrom(dll); } catch { }
        }
        var sts2Asm = Assembly.LoadFrom(sts2Path);
        var ritsuAsm = Assembly.LoadFrom(ritsuLibPath);

        var allAssemblies = new List<Assembly> { sts2Asm, ritsuAsm };
        IEnumerable<Type> AllTypes() => allAssemblies.SelectMany(a => { try { return a.GetTypes(); } catch { return Array.Empty<Type>(); } });

        // 1. ALL generic methods named "Apply" (ONLY generic ones)
        Console.WriteLine("=== ALL Generic Apply methods ===");
        foreach (var t in AllTypes())
        {
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.Instance))
            {
                if (m.Name == "Apply" && m.IsGenericMethod)
                {
                    var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                    var generics = string.Join(", ", m.GetGenericArguments().Select(g => g.Name));
                    Console.WriteLine($"  {t.FullName}.Apply<{generics}>({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}]");
                }
            }
        }

        // 2. DamageCmd class
        Console.WriteLine("\n=== DamageCmd ===");
        foreach (var t in AllTypes().Where(t => t.Name == "DamageCmd"))
        {
            Console.WriteLine($"  Type: {t.FullName}");
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.Instance))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                var generic = m.IsGenericMethod ? $"<{string.Join(", ", m.GetGenericArguments().Select(g => g.Name))}>" : "";
                Console.WriteLine($"  {m.Name}{generic}({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}]");
            }
        }

        // 3. AttackCommand ALL methods (including builder methods)
        Console.WriteLine("\n=== AttackCommand ALL methods ===");
        foreach (var t in AllTypes().Where(t => t.Name == "AttackCommand"))
        {
            Console.WriteLine($"  Type: {t.FullName}");
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}" + (p.HasDefaultValue ? $" = {p.DefaultValue}" : "")));
                Console.WriteLine($"  {m.Name}({parms}) -> {m.ReturnType.Name}");
            }
        }

        // 4. Check if PowerCmd has any generic methods at all
        Console.WriteLine("\n=== PowerCmd ALL methods (including generic) ===");
        foreach (var t in AllTypes().Where(t => t.Name == "PowerCmd"))
        {
            Console.WriteLine($"  Type: {t.FullName}");
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.Instance))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}" + (p.HasDefaultValue ? $" = {p.DefaultValue}" : "")));
                var generic = m.IsGenericMethod ? $"<{string.Join(", ", m.GetGenericArguments().Select(g => g.Name))}>" : "";
                Console.WriteLine($"  {m.Name}{generic}({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}]");
            }
        }

        // 5. Check if there are extension methods for PowerCmd in RitsuLib
        Console.WriteLine("\n=== RitsuLib extension methods for Creature or PowerCmd ===");
        foreach (var t in ritsuAsm.GetTypes())
        {
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Static))
            {
                if (m.IsDefined(typeof(System.Runtime.CompilerServices.ExtensionAttribute), false))
                {
                    var parms = m.GetParameters();
                    if (parms.Length > 0 && (parms[0].ParameterType.Name == "Creature" || parms[0].ParameterType.Name == "PowerCmd" || m.Name.Contains("Apply") || m.Name.Contains("Power")))
                    {
                        var parmStr = string.Join(", ", parms.Select(p => $"{p.ParameterType.Name} {p.Name}" + (p.HasDefaultValue ? $" = {p.DefaultValue}" : "")));
                        var generic = m.IsGenericMethod ? $"<{string.Join(", ", m.GetGenericArguments().Select(g => g.Name))}>" : "";
                        Console.WriteLine($"  {t.FullName}.{m.Name}{generic}({parmStr}) -> {m.ReturnType.Name} [Extension]");
                    }
                }
            }
        }

        // 6. Inspect ModCardTemplate and CardModel for exhaust-related members
        Console.WriteLine("\n=== ModCardTemplate and CardModel properties ===");
        foreach (var t in AllTypes().Where(t => t.Name == "ModCardTemplate" || t.Name == "CardModel" || t.Name == "Card"))
        {
            Console.WriteLine($"\n  Type: {t.FullName} (IsInterface={t.IsInterface})");
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static);
            Console.WriteLine("  -- All Properties --");
            foreach (var p in props)
            {
                Console.WriteLine($"    {p.Name} : {p.PropertyType.Name} (CanRead={p.CanRead}, CanWrite={p.CanWrite})");
            }
            Console.WriteLine("  -- All Methods (non-inherited) --");
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                var generic = m.IsGenericMethod ? $"<{string.Join(", ", m.GetGenericArguments().Select(g => g.Name))}>" : "";
                Console.WriteLine($"    {m.Name}{generic}({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}]");
            }
            Console.WriteLine("  -- Exhaust-related members --");
            foreach (var p in props.Where(p => p.Name.Contains("Exhaust") || p.Name.Contains("Ethereal") || p.Name.Contains("Keyword")))
            {
                Console.WriteLine($"    PROP: {p.Name} : {p.PropertyType.Name} (CanRead={p.CanRead}, CanWrite={p.CanWrite})");
            }
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static).Where(m => m.Name.Contains("Exhaust") || m.Name.Contains("Keyword")))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"    METHOD: {m.Name}({parms}) -> {m.ReturnType.Name}");
            }
        }

        // 7. Check CardKeyword enum
        Console.WriteLine("\n=== CardKeyword enum values ===");

        // 7a. Check EnergyCost / Cost-related members on ModCardTemplate/CardModel
        Console.WriteLine("\n=== Cost-related members on Card types ===");
        foreach (var t in AllTypes().Where(t => t.Name == "ModCardTemplate" || t.Name == "CardModel" || t.Name == "Card"))
        {
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static);
            foreach (var p in props.Where(p => p.Name.Contains("Cost") || p.Name.Contains("Energy") || p.Name.Contains("Price")))
            {
                Console.WriteLine($"  {t.Name}.PROP: {p.Name} : {p.PropertyType.Name} (CanRead={p.CanRead}, CanWrite={p.CanWrite})");
            }
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static).Where(m => m.Name.Contains("Cost") || m.Name.Contains("Energy") || m.Name.Contains("Price") || m.Name.Contains("Upgrade")))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"  {t.Name}.METHOD: {m.Name}({parms}) -> {m.ReturnType.Name}");
            }
        }

        // 7b. Check DynamicVar subtypes
        Console.WriteLine("\n=== DynamicVar subtypes ===");
        foreach (var t in AllTypes().Where(t => typeof(object).IsAssignableFrom(t) && t.Name.Contains("Var")))
        {
            if (t.IsAbstract || t.IsInterface) continue;
            Console.WriteLine($"  {t.FullName} (Base: {t.BaseType?.Name})");
        }

        // 7c. Check Upgrade-related methods
        Console.WriteLine("\n=== Upgrade-related on ModCardTemplate ===");

        // 7d. Check CardEnergyCost type
        Console.WriteLine("\n=== CardEnergyCost type ===");
        foreach (var t in AllTypes().Where(t => t.Name == "CardEnergyCost"))
        {
            Console.WriteLine($"  Type: {t.FullName}");
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static);
            foreach (var p in props)
            {
                Console.WriteLine($"    PROP: {p.Name} : {p.PropertyType.Name} (CanRead={p.CanRead}, CanWrite={p.CanWrite})");
            }
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"    METHOD: {m.Name}({parms}) -> {m.ReturnType.Name} [Virtual={m.IsVirtual}]");
            }
        }

        // 7e. Check CardUpgradePreviewType enum
        Console.WriteLine("\n=== CardUpgradePreviewType enum ===");
        foreach (var t in AllTypes().Where(t => t.Name == "CardUpgradePreviewType"))
        {
            Console.WriteLine($"  Type: {t.FullName} (IsEnum={t.IsEnum})");
            if (t.IsEnum)
            {
                foreach (var v in Enum.GetValues(t))
                {
                    Console.WriteLine($"    {v} = {Convert.ToInt32(v)}");
                }
            }
        }

        // 7f. Check ModCardTemplate OnUpgrade / UpgradeCost methods
        Console.WriteLine("\n=== ModCardTemplate declared methods (all) ===");
        foreach (var t in AllTypes().Where(t => t.Name == "ModCardTemplate"))
        {
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                var generic = m.IsGenericMethod ? $"<{string.Join(", ", m.GetGenericArguments().Select(g => g.Name))}>" : "";
                Console.WriteLine($"  {m.Name}{generic}({parms}) -> {m.ReturnType.Name} [Virtual={m.IsVirtual}]");
            }
        }

        foreach (var t in AllTypes().Where(t => t.Name == "CardKeyword" || t.Name == "CardTraits"))
        {
            Console.WriteLine($"  Type: {t.FullName} (IsEnum={t.IsEnum})");
            if (t.IsEnum)
            {
                foreach (var v in Enum.GetValues(t))
                {
                    Console.WriteLine($"    {v} = {Convert.ToInt32(v)}");
                }
            }
            else
            {
                var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static);
                foreach (var p in props)
                {
                    Console.WriteLine($"    {p.Name} : {p.PropertyType.Name}");
                }
            }
        }

        // 8. Player class - all properties and methods
        Console.WriteLine("\n=== Player class ===");
        foreach (var t in AllTypes().Where(t => t.Name == "Player"))
        {
            Console.WriteLine($"  Type: {t.FullName} (IsInterface={t.IsInterface})");
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static);
            Console.WriteLine("  -- All Properties --");
            foreach (var p in props)
            {
                Console.WriteLine($"    {p.Name} : {p.PropertyType.Name} (CanRead={p.CanRead}, CanWrite={p.CanWrite})");
            }
            Console.WriteLine("  -- All Methods (declared only) --");
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                var generic = m.IsGenericMethod ? $"<{string.Join(", ", m.GetGenericArguments().Select(g => g.Name))}>" : "";
                Console.WriteLine($"    {m.Name}{generic}({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}, Virtual={m.IsVirtual}]");
            }
            Console.WriteLine("  -- Energy-related members --");
            foreach (var p in props.Where(p => p.Name.Contains("Energy") || p.Name.Contains("Cost") || p.Name.Contains("Mana")))
            {
                Console.WriteLine($"    PROP: {p.Name} : {p.PropertyType.Name} (CanRead={p.CanRead}, CanWrite={p.CanWrite})");
            }
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static).Where(m => m.Name.Contains("Energy") || m.Name.Contains("Mana") || m.Name.Contains("Cost")))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"    METHOD: {m.Name}({parms}) -> {m.ReturnType.Name}");
            }
        }

        // 9. All types with "Energy" in their name
        Console.WriteLine("\n=== All types with 'Energy' in name ===");
        foreach (var t in AllTypes().Where(t => t.Name.Contains("Energy")))
        {
            Console.WriteLine($"  {t.FullName} (IsClass={t.IsClass}, IsEnum={t.IsEnum}, IsInterface={t.IsInterface})");
            if (!t.IsEnum && !t.IsInterface)
            {
                var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static);
                foreach (var p in props)
                {
                    Console.WriteLine($"    PROP: {p.Name} : {p.PropertyType.Name}");
                }
                foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly))
                {
                    var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                    var generic = m.IsGenericMethod ? $"<{string.Join(", ", m.GetGenericArguments().Select(g => g.Name))}>" : "";
                    Console.WriteLine($"    METHOD: {m.Name}{generic}({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}]");
                }
            }
            if (t.IsEnum)
            {
                foreach (var v in Enum.GetValues(t))
                {
                    Console.WriteLine($"    {v} = {Convert.ToInt32(v)}");
                }
            }
        }

        // 10. All types in MegaCrit.Sts2.Core.Commands namespace
        Console.WriteLine("\n=== All types in MegaCrit.Sts2.Core.Commands ===");
        foreach (var t in AllTypes().Where(t => t.Namespace == "MegaCrit.Sts2.Core.Commands").OrderBy(t => t.Name))
        {
            Console.WriteLine($"  {t.Name} (IsClass={t.IsClass}, IsInterface={t.IsInterface}, IsStatic={t.IsAbstract && t.IsSealed})");
        }

        // 11. All static method signatures in Commands namespace
        Console.WriteLine("\n=== All static methods in Commands namespace ===");
        foreach (var t in AllTypes().Where(t => t.Namespace != null && t.Namespace.StartsWith("MegaCrit.Sts2.Core.Commands")).OrderBy(t => t.Name))
        {
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}" + (p.HasDefaultValue ? $" = {p.DefaultValue}" : "")));
                var generic = m.IsGenericMethod ? $"<{string.Join(", ", m.GetGenericArguments().Select(g => g.Name))}>" : "";
                Console.WriteLine($"  {t.Name}.{m.Name}{generic}({parms}) -> {m.ReturnType.Name}");
            }
        }

        // 13. Check ModPowerTemplate and PowerModel for all hooks
        Console.WriteLine("\n=== ModPowerTemplate and PowerModel hooks ===");
        foreach (var t in AllTypes().Where(t => t.Name == "ModPowerTemplate" || t.Name == "PowerModel" || t.Name == "Power"))
        {
            Console.WriteLine($"\n  Type: {t.FullName} (IsInterface={t.IsInterface})");
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static);
            Console.WriteLine("  -- All Properties --");
            foreach (var p in props)
            {
                Console.WriteLine($"    {p.Name} : {p.PropertyType.Name} (CanRead={p.CanRead}, CanWrite={p.CanWrite})");
            }
            Console.WriteLine("  -- All Methods (declared only) --");
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}" + (p.HasDefaultValue ? $" = {p.DefaultValue}" : "")));
                var generic = m.IsGenericMethod ? $"<{string.Join(", ", m.GetGenericArguments().Select(g => g.Name))}>" : "";
                Console.WriteLine($"    {m.Name}{generic}({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}, Virtual={m.IsVirtual}]");
            }
        }

        // 12. All types with "Cmd" in their name
        Console.WriteLine("\n=== All types with 'Cmd' in name ===");
        foreach (var t in AllTypes().Where(t => t.Name.Contains("Cmd")).OrderBy(t => t.Name))
        {
            Console.WriteLine($"  {t.FullName}");
            foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly))
            {
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}" + (p.HasDefaultValue ? $" = {p.DefaultValue}" : "")));
                var generic = m.IsGenericMethod ? $"<{string.Join(", ", m.GetGenericArguments().Select(g => g.Name))}>" : "";
                Console.WriteLine($"    {m.Name}{generic}({parms}) -> {m.ReturnType.Name} [Static]");
            }
        }
    }
}
