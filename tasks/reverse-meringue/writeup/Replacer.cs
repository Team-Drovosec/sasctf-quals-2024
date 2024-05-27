using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using dnlib.DotNet.Writer;
namespace dnlib.Examples {
	public class Example3 {

		public static void Run() {
            Dictionary<int, Dictionary<int, KeyValuePair<int, int>>> unflatteningMapping = new Dictionary<int, Dictionary<int, KeyValuePair<int, int>>>();

            var lines = File.ReadAllLines(@"log_ida.txt");
            foreach (var line in lines) {
                string line1 = line.Replace("0x", "").Replace("L", "").Replace("[", "").Replace("]", "") ;
                string[] entries = line1.Split(' ');

                int identifer = Convert.ToInt32(entries[0], 16);
                unflatteningMapping[identifer] = new Dictionary<int, KeyValuePair<int, int>>();

                for (int i = 1; i < entries.Length; i++) {
                    string[] split_entry = entries[i].Split(',');
                    int switch_id = Convert.ToInt32(split_entry[0], 16);
                    int mul_numb = Convert.ToInt32(split_entry[1], 16);
                    int xor_numb = Convert.ToInt32(split_entry[2], 16);
                    unflatteningMapping[identifer][switch_id] = new KeyValuePair<int, int>(mul_numb, xor_numb);

                }
              
            }
            ModuleDefMD mod = ModuleDefMD.Load(@"broken.exe");
            foreach (TypeDef type in mod.GetTypes()) {
                foreach (MethodDef method in type.Methods) {
                    if (method.HasBody) {
                        var insns = method.Body.Instructions;
                        int i = 0;
                        while (i < insns.Count - 4) {
                            if (insns[i].GetOpCode() == OpCodes.Ldc_I4
                                && insns[i + 1].GetOpCode() == OpCodes.Ldc_I4
                                && insns[i + 2].GetOpCode() == OpCodes.Xor
                                && insns[i + 3].GetOpCode() == OpCodes.Dup
                                && insns[i + 4].GetOpCode().ToString().Contains("tloc")
                                ) {
                                int functionIdent = (int)insns[i].Operand;
                                if (unflatteningMapping.ContainsKey(functionIdent)) {
                                    Dictionary<int, KeyValuePair<int, int>> valuesToReplace = unflatteningMapping[functionIdent];
                                    while (insns[i].GetOpCode() != OpCodes.Switch) {
                                        i++;
                                    }
                                    Instruction[] operand = (Instruction[])insns[i].Operand;

                                    foreach (int switchValue in valuesToReplace.Keys) {
                                        KeyValuePair<int, int> switchValuePair = valuesToReplace[switchValue];
                                        int mulVal = switchValuePair.Key;
                                        int xorVal = switchValuePair.Value;
                                        int switchDestOffset = (int)operand[switchValue].Offset;
                                        int insnIdx = 0;
                                        for (int k = 0; k < insns.Count; k++) {
                                            if (insns[k].Offset == switchDestOffset) {
                                                insnIdx = k;
                                                break;
                                            }
                                        }

                                        while (!(insnIdx < insns.Count && insns[insnIdx].GetOpCode() == OpCodes.Ldc_I4 
                                            && insns[insnIdx + 1].GetOpCode() == OpCodes.Mul
                                            && insns[insnIdx + 2].GetOpCode() == OpCodes.Ldc_I4
                                            && insns[insnIdx + 3].GetOpCode() == OpCodes.Xor)) {
                                            insnIdx++;
                                        }
                                        if (insns[insnIdx].GetOpCode() == OpCodes.Ldc_I4) {
                                            insns[insnIdx].Operand = mulVal;
                                            insns[insnIdx + 2].Operand = xorVal;
                                        } else {
                                            Console.WriteLine("Warning: " + functionIdent.ToString() + " wrong instruction index!");
                                        }


                                    }

                                } else {
                                    Console.WriteLine("Warning: " + functionIdent.ToString() + " was not in unflattening dict!");
                                }
                            }
                            i++;

                        }
                    }
                }
            }
            ModuleWriterOptions options = new ModuleWriterOptions(mod);
            options.MetaDataOptions.Flags = MetaDataFlags.PreserveAll | MetaDataFlags.KeepOldMaxStack;
            mod.Write(@"deobfsucated.exe", options);
            return;
        }

	}
    
}
