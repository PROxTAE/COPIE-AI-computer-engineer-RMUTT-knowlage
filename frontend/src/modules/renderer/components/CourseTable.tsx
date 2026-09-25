// ตารางรายวิชา — ม็อกอัพ 07-course-table
// เดสก์ท็อปเป็นตารางเรียงคอลัมน์ได้ มือถือเป็นรายการการ์ด
// คลิกแถวเพื่อดูรายละเอียดวิชาใต้ตาราง ปิดท้ายด้วยแถบรวมหน่วยกิตตัวเลขใหญ่
"use client";

import { useState } from "react";
import { BarChart3, ChevronDown, ChevronRight, FileText } from "lucide-react";
import { motion } from "motion/react";
import type { Course, CourseTableData } from "@/types/contract";

type SortKey = "code" | "name_th" | "credits" | "category";
type SortDirection = "asc" | "desc";

const COLUMNS: { key: SortKey; label: string; align: "left" | "right" }[] = [
  { key: "code", label: "รหัส", align: "left" },
  { key: "name_th", label: "รายวิชา", align: "left" },
  { key: "credits", label: "หน่วยกิต", align: "right" },
  { key: "category", label: "หมวด", align: "left" },
];

export function CourseTable({
  data,
  disabled = false,
  animate = true,
}: {
  data: CourseTableData;
  disabled?: boolean;
  animate?: boolean;
}) {
  const [sort, setSort] = useState<{ key: SortKey; direction: SortDirection } | null>(null);
  const [selected, setSelected] = useState<string | null>(null);

  const courses = sort ? sortCourses(data.courses, sort.key, sort.direction) : data.courses;
  const selectedCourse = courses.find((course) => course.code === selected) ?? null;

  const toggleSort = (key: SortKey) =>
    setSort((current) =>
      current?.key === key && current.direction === "asc" ? { key, direction: "desc" } : { key, direction: "asc" },
    );

  const toggleRow = (code: string) => setSelected((current) => (current === code ? null : code));

  const heading = `รายวิชา ปี ${data.year} เทอม ${data.semester}`;

  // API จริงอาจคืนเทอมที่ไม่มีรายวิชา อย่าปล่อยให้ผู้ใช้เห็นหัวตารางเปล่า ๆ
  if (data.courses.length === 0) {
    return (
      <section className="copie-panel flex flex-col gap-4" aria-label={heading}>
        <h2 className="copie-heading flex items-center gap-3 font-display text-2xl font-bold text-deep-navy">
          <span aria-hidden="true" className="h-8 w-1 shrink-0 rounded-full bg-copie-teal" />
          {heading}
        </h2>
        <p className="rounded-xl border border-deep-navy/12 bg-surface px-4 py-6 text-center text-muted">
          ไม่พบรายวิชาของปีและเทอมนี้ในเล่มหลักสูตร
        </p>
      </section>
    );
  }

  return (
    <section className="copie-panel flex flex-col gap-4" aria-label={`รายวิชา ปี ${data.year} เทอม ${data.semester}`}>
      <h2 className="copie-heading flex items-center gap-3 font-display text-2xl font-bold text-deep-navy">
        <span aria-hidden="true" className="h-8 w-1 shrink-0 rounded-full bg-copie-teal" />
        รายวิชา ปี {data.year} เทอม {data.semester}
      </h2>

      {/* เดสก์ท็อป: ตารางจริง เลื่อนแนวนอนในกล่องตัวเองได้เมื่อจอแคบ */}
      <div className="hidden overflow-x-auto rounded-xl border border-deep-navy/12 @2xl:block">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-mist/60">
              {COLUMNS.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  aria-sort={
                    sort?.key === column.key ? (sort.direction === "asc" ? "ascending" : "descending") : "none"
                  }
                  className={`px-4 py-3 font-semibold text-deep-navy ${
                    column.align === "right" ? "text-right" : "text-left"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => toggleSort(column.key)}
                    disabled={disabled}
                    className="inline-flex items-center gap-1 rounded disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-copie-teal"
                  >
                    {column.label}
                    <ChevronDown
                      aria-hidden="true"
                      className={`size-3.5 transition-transform ${
                        sort?.key === column.key ? "text-copie-teal" : "text-muted"
                      } ${sort?.key === column.key && sort.direction === "desc" ? "rotate-180" : ""}`}
                    />
                  </button>
                </th>
              ))}
              <th scope="col" className="w-10 px-2 py-3">
                <span className="sr-only">ดูรายละเอียด</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {courses.map((course, index) => {
              const active = course.code === selected;
              return (
                <motion.tr
                  key={course.code}
                  initial={animate ? { opacity: 0, y: 6 } : false}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: animate ? index * 0.04 : 0 }}
                  onClick={() => toggleRow(course.code)}
                  data-selected={active}
                  className={`cursor-pointer border-t border-deep-navy/8 transition ${
                    active ? "bg-copie-teal/8" : "hover:bg-mist/50"
                  }`}
                >
                  <td className="relative whitespace-nowrap px-4 py-3 tabular-nums text-ink">
                    {active && <span aria-hidden="true" className="absolute inset-y-0 left-0 w-1 bg-copie-teal" />}
                    <span className={active ? "font-semibold text-deep-navy" : ""}>{course.code}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`block ${active ? "font-semibold text-deep-navy" : "text-ink"}`}>
                      {course.name_th}
                    </span>
                    <span className="block text-xs text-muted">{course.name_en}</span>
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-ink">{course.credits}</td>
                  <td className="px-4 py-3 text-ink">{course.category ?? "—"}</td>
                  <td className="px-2 py-3 text-right">
                    {/* ปุ่มจริงเพื่อให้กดด้วยคีย์บอร์ดได้ — แถวทั้งแถวกดได้เฉพาะด้วยเมาส์ */}
                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        toggleRow(course.code);
                      }}
                      aria-expanded={active}
                      aria-label={`ดูรายละเอียด ${course.name_th}`}
                      className="rounded focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-copie-teal"
                    >
                      <ChevronRight
                        aria-hidden="true"
                        className={`inline size-4 transition-transform ${
                          active ? "rotate-90 text-copie-teal" : "text-muted"
                        }`}
                      />
                    </button>
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* มือถือ: การ์ดต่อหนึ่งวิชา กดที่การ์ดเพื่อกางรายละเอียด */}
      <ul className="flex flex-col gap-2 @2xl:hidden">
        {courses.map((course, index) => {
          const active = course.code === selected;
          return (
            <motion.li
              key={course.code}
              initial={animate ? { opacity: 0, y: 6 } : false}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: animate ? index * 0.04 : 0 }}
            >
              <button
                type="button"
                onClick={() => toggleRow(course.code)}
                aria-expanded={active}
                className={`flex w-full flex-col gap-1 rounded-lg border p-3 text-left transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-copie-teal ${
                  active ? "border-copie-teal bg-copie-teal/8" : "border-deep-navy/12 bg-surface"
                }`}
              >
                <span className="flex items-center justify-between gap-2">
                  <span className="text-sm font-semibold tabular-nums text-deep-navy">{course.code}</span>
                  <span className="text-sm tabular-nums text-ink">{course.credits} หน่วยกิต</span>
                </span>
                <span className="text-sm text-ink">{course.name_th}</span>
                <span className="text-xs text-muted">{course.name_en}</span>
                {course.category && <span className="text-xs text-muted">{course.category}</span>}
              </button>
            </motion.li>
          );
        })}
      </ul>

      {selectedCourse && <CourseDetail course={selectedCourse} />}

      <div className="flex flex-wrap items-center gap-3 rounded-xl border border-copie-teal/25 bg-copie-teal/8 px-4 py-3">
        <BarChart3 aria-hidden="true" className="size-5 text-copie-teal" />
        <span className="font-display font-semibold text-deep-navy">รวมหน่วยกิตทั้งสิ้น</span>
        <span className="copie-index font-display text-3xl font-bold italic tabular-nums text-copie-teal">
          {data.total_credits}
        </span>
        <span className="text-deep-navy">หน่วยกิต</span>
        <span className="ml-auto text-xs text-muted tabular-nums">{data.courses.length} รายวิชา</span>
      </div>
    </section>
  );
}

function CourseDetail({ course }: { course: Course }) {
  return (
    <div className="flex gap-3 rounded-xl border border-deep-navy/12 bg-surface p-4">
      <FileText aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-copie-teal" />
      <div className="min-w-0">
        <p className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
          <span className="font-display font-bold tabular-nums text-deep-navy">{course.code}</span>
          <span className="font-display font-semibold text-deep-navy">{course.name_th}</span>
          <span className="text-sm text-muted">{course.name_en}</span>
        </p>
        <p className="mt-1 text-sm leading-6 text-ink">
          {course.description ?? "ยังไม่มีคำอธิบายรายวิชาในเล่มหลักสูตร"}
        </p>
        <p className="mt-2 text-xs text-muted tabular-nums">
          {course.credits} หน่วยกิต
          {course.credit_detail ? ` · ${course.credit_detail}` : ""}
          {course.category ? ` · ${course.category}` : ""}
        </p>
      </div>
    </div>
  );
}

function sortCourses(courses: Course[], key: SortKey, direction: SortDirection): Course[] {
  const factor = direction === "asc" ? 1 : -1;
  return [...courses].sort((a, b) => {
    if (key === "credits") return (a.credits - b.credits) * factor;
    // category เป็น null ได้ — ดันไปท้ายตารางเสมอไม่ว่าจะเรียงทางไหน
    const left = a[key] ?? "";
    const right = b[key] ?? "";
    if (left === right) return 0;
    if (left === "") return 1;
    if (right === "") return -1;
    return left.localeCompare(right, "th") * factor;
  });
}
